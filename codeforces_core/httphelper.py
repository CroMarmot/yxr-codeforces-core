import logging
from typing import Any, Callable, Dict, Tuple

# from . import config
from .constants import CF_HOST
from lxml import html
from os import path
import asyncio
import aiohttp
import pyaes
import json
import re

from .interfaces.AioHttpHelper import AioHttpHelperInterface

default_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip',
    # 'User-Agent': config.conf['user_agent'], TODO
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

# session: aiohttp.ClientSession = None
# tokens = {}
# cookie_jar = None

logger = logging.getLogger(__name__)


class RCPCRedirectionError(Exception):

  def __init__(self):
    super().__init__("RCPC redirection detected")


def add_header(newhdr, headers=default_headers) -> Dict[str, str]:
  headers.update(newhdr)
  return headers


# def get(url, headers=None, csrf=False):
#   resp = asyncio.run(async_get(url, headers, csrf))
#   if resp:
#     return resp[0]
#   else:
#     return None
#
#
# def post(url, data, headers=None, csrf=False):
#   resp = asyncio.run(async_post(url, data, headers, csrf))
#   if resp:
#     return resp[0]
#   else:
#     return None
#
#
# def GET(url, headers=None, csrf=False):
#   return {'method': async_get, 'url': url, 'headers': headers, 'csrf': csrf}
#
#
# def POST(url, data, headers=None, csrf=False):
#   return {'method': async_post, 'url': url, 'data': data, 'headers': headers, 'csrf': csrf}

# def urlsopen(urls):
#   return asyncio.run(async_urlsopen(urls))
#
#
# async def async_urlsopen(urls):
#   tasks = []
#   for u in urls:
#     if u['method'] == async_get:
#       tasks += [async_get(u['url'], u['headers'], u['csrf'])]
#     elif u['method'] == async_post:
#       tasks += [async_post(u['url'], u['data'], u['headers'], u['csrf'])]
#   return await asyncio.gather(*tasks)
#
#
# async def on_request_start(session, trace_request_ctx, params):
#   trace_request_ctx.start = asyncio.get_event_loop().time()
#   print(session)
#   print("[*] Request start : {}".format(params))


async def on_request_chunk_sent(session, trace_request_ctx, params):
  print("[*] Request sent chunk : {}".format(params.chunk))


async def on_request_end(session, trace_request_ctx, params):
  elapsed = asyncio.get_event_loop().time() - trace_request_ctx.start
  print("[*] Request end : {}".format(elapsed))


class HttpHelper(AioHttpHelperInterface):
  session = {}
  cookie_jar_path = ''
  cookie_jar = None
  token_path = ''
  tokens = {}
  headers = {}  # TODO

  def __init__(self, cookie_jar_path: str = '', token_path: str = '', headers=default_headers, host=CF_HOST) -> None:
    # if path is empty string then won't save to any file, just store in memory
    self.cookie_jar_path = cookie_jar_path
    # if path is empty string then won't save to any file, just store in memory
    self.token_path = token_path
    self.headers = headers
    # TODO support cf mirror site?
    self.host = host

  @staticmethod
  def load_tokens(token_path: str) -> Dict[str, Any]:
    if path.isfile(token_path):
      with open(token_path, 'r') as f:
        return json.load(f)
    return {}

  @staticmethod
  def load_cookie_jar(cookie_jar_path: str) -> aiohttp.CookieJar:
    jar = aiohttp.CookieJar()
    if cookie_jar_path:
      if path.isfile(cookie_jar_path):
        jar.load(file_path=cookie_jar_path)
      # else:
      #   jar.save(file_path=cookie_jar_path)
    return jar

  async def open_session(self) -> aiohttp.ClientSession:
    self.cookie_jar = HttpHelper.load_cookie_jar(self.cookie_jar_path)
    self.tokens = HttpHelper.load_tokens(self.token_path)
    # if config.conf['trace_requests']:
    #   cfg = aiohttp.TraceConfig()
    #   cfg.on_request_start.append(on_request_start)
    #   cfg.on_request_chunk_sent.append(on_request_chunk_sent)
    #   cfg.on_request_end.append(on_request_end)
    #   trace_config = [cfg]
    # else:
    #   trace_config = []
    trace_config = []
    self.session = await aiohttp.ClientSession(cookie_jar=self.cookie_jar, trace_configs=trace_config).__aenter__()
    return self.session

  async def close_session(self) -> None:
    await self.session.__aexit__(None, None, None)
    self.tokens = {}
    self.cookie_jar = {}
    self.session = None

  def update_tokens(self, csrf: str, ftaa: str, bfaa: str, uc: str, usmc: str) -> None:
    self.tokens = {'csrf': csrf[:32], 'ftaa': ftaa, 'bfaa': bfaa, 'uc': uc, 'usmc': usmc}
    if self.token_path:
      with open(self.token_path, 'w') as f:
        json.dump(self.tokens, f)

  async def async_get(self, url, headers=None, csrf=False):
    if headers == None: headers = default_headers
    if csrf and 'csrf' in self.tokens:
      headers = add_header({'X-Csrf-Token': self.tokens['csrf']})
    # TODO remove the feature
    if url.startswith('/'): url = self.host + url
    result = None
    try:
      async with self.session.get(url, headers=headers) as response:
        assert response.status == 200
        self.check_rcpc(await response.text())
        if self.cookie_jar_path:
          self.cookie_jar.save(file_path=self.cookie_jar_path)  # TODO move auto save to file out
        return await response.text()
    except RCPCRedirectionError:
      async with self.session.get(url, headers=headers) as response:
        assert response.status == 200
        if self.cookie_jar_path:
          self.cookie_jar.save(file_path=self.cookie_jar_path)
        return await response.text()

  async def async_post(self, url, data, headers=None, csrf=False):
    if headers == None: headers = default_headers
    if csrf and 'csrf' in self.tokens:
      headers = add_header({'X-Csrf-Token': self.tokens['csrf']})

    # TODO remove the feature
    if url.startswith('/'): url = self.host + url
    result = None
    try:
      async with self.session.post(url, headers=headers, data=data) as response:
        assert response.status == 200
        self.check_rcpc(await response.text())
        if self.cookie_jar_path:
          self.cookie_jar.save(file_path=self.cookie_jar_path)
        return await response.text()
    except RCPCRedirectionError:
      async with self.session.post(url, headers=headers, data=data) as response:
        assert response.status == 200
        if self.cookie_jar_path:
          self.cookie_jar.save(file_path=self.cookie_jar_path)
        return await response.text()

  def get_tokens(self):
    return self.tokens

  def check_rcpc(self, html_data: str):
    doc = html.fromstring(html_data)
    aesmin = doc.xpath(".//script[@type='text/javascript' and @src='/aes.min.js']")
    if len(aesmin) > 0:
      print("[+] RCPC redirection detected")
      js = doc.xpath(".//script[not(@type)]")
      assert len(js) > 0
      keys = re.findall(r'[abc]=toNumbers\([^\)]*', js[0].text)
      for k in keys:
        if k[0] == 'a':
          key = bytes.fromhex(k.split('"')[1])
        elif k[0] == 'b':
          iv = bytes.fromhex(k.split('"')[1])
        elif k[0] == 'c':
          ciphertext = bytes.fromhex(k.split('"')[1])
      assert len(key) == 16 and len(iv) == 16 and len(ciphertext) == 16, 'AES decryption error'
      c = pyaes.AESModeOfOperationCBC(key, iv=iv)
      plaintext = c.decrypt(ciphertext)
      rcpc = plaintext.hex()
      self.cookie_jar.update_cookies({'RCPC': rcpc})
      self.cookie_jar.save(file_path=self.cookie_jar_path)
      raise RCPCRedirectionError()

  def create_form(self, form_data) -> aiohttp.FormData:
    form = aiohttp.FormData()
    for k, v in form_data.items():
      form.add_field(k, v)
    return form

  # callback return (end watch?, transform result)
  async def websockets(self, url: str, callback: Callable[[Any], Tuple[bool, Any]]) -> Any:
    try:
      async with self.session.ws_connect(url) as ws:
        ret = []
        async for msg in ws:
          if msg.type == aiohttp.WSMsgType.TEXT:
            js = json.loads(msg.data)
            js['text'] = json.loads(js['text'])

            endwatch, obj = callback(js)
            ret.append(obj)
            if endwatch:
              return ret

          else:
            logger.error('wrong msg type?', msg.type)
            break
        return ret
    except Exception as e:
      logger.error(e)
      # session closed?
      return False
