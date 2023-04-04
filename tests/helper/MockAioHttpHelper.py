import asyncio
import os
import re
import aiohttp
from typing import Any, Callable, Dict

from codeforces_core.interfaces.AioHttpHelper import AioHttpHelperInterface
from ..constant import test_dir

# The key is regex str instead of str
GET_MOCK_LIST: Dict[str, str] = {
    'logged-codeforces\\.com': 'logged-codeforces.com.html',
    'notlogged-codeforces\\.com': 'notlogged-codeforces.com.html',
    'https://codeforces.com/enter\\?back=%2F': 'notlogged-codeforces.com.html',
    'https://codeforces.com/contest/1777/my': 'contest_1777_submission.html',
}

# The key is regex str instead of str
POST_MOCK_LIST: Dict[str, str] = {
    'https://codeforces.com/enter\\?back=%2F': 'logged-codeforces.com.html',
    '/contest/.*/problem/.*': 'contest_1777_submission.html',
}

# The key is regex str instead of str
WS_MOCK_LIST: Dict[str, str] = {
    "wss://pubsub.codeforces.com/ws/s_.*/s_.*": "ws_contest_submission.text",
}

# TODO use Annotation
BEFORE_UPDATE_TOKENS = 'before:update_tokens'
BEFORE_OPEN_SESSION = 'before:open_session'
BEFORE_CLOSE_SESSION = 'before:close_session'
BEFORE_GET_TOKENS = 'before:get_tokens'
BEFORE_ASYNC_GET = 'before:async_get'
BEFORE_ASYNC_POST = 'before:async_post'


class MockAioHttpHelper(AioHttpHelperInterface):

  def __init__(self) -> None:
    super().__init__()
    self.listeners = {}

  def create_form(form_data: Dict[str, Any]) -> aiohttp.FormData:
    assert (False)

  async def async_get(self, url: str) -> str:
    if BEFORE_ASYNC_GET in self.listeners:
      for fn in self.listeners[BEFORE_ASYNC_GET]:
        fn(url)

    for k, v in GET_MOCK_LIST.items():
      if re.match(k, url):
        path = os.path.join(test_dir, 'unit/mock', GET_MOCK_LIST[k])
        with open(path, 'r') as f:
          return f.read()
    # No url matched
    print(url)
    assert (False)

  async def async_post(self, url: str, post_data: Dict[str, Any]) -> str:
    if BEFORE_ASYNC_POST in self.listeners:
      for fn in self.listeners[BEFORE_ASYNC_POST]:
        fn(url, post_data)

    for k, v in POST_MOCK_LIST.items():
      if re.match(k, url):
        path = os.path.join(test_dir, 'unit/mock', POST_MOCK_LIST[k])
        with open(path, 'r') as f:
          return f.read()
    # No url matched
    print("POST", url)
    assert (False)

  def update_tokens(self, csrf: str, ftaa: str, bfaa: str, uc: str, usmc: str) -> None:
    if BEFORE_UPDATE_TOKENS in self.listeners:
      for fn in self.listeners[BEFORE_UPDATE_TOKENS]:
        fn(csrf, ftaa, bfaa, uc, usmc)

  async def open_session(self) -> aiohttp.ClientSession:
    if BEFORE_OPEN_SESSION in self.listeners:
      for fn in self.listeners[BEFORE_OPEN_SESSION]:
        fn()
    # self.cookie_jar = HttpHelper.load_cookie_jar(self.cookie_jar_path)
    self.tokens = {'csrf': "mock_csrf", 'ftaa': "mock_ftaa", 'bfaa': "mock_bfaa", 'uc': "mock_uc", 'usmc': "mock_usmc"}
    # self.session = await aiohttp.ClientSession(cookie_jar=self.cookie_jar, trace_configs=trace_config).__aenter__()

  async def close_session(self) -> None:
    if BEFORE_CLOSE_SESSION in self.listeners:
      for fn in self.listeners[BEFORE_CLOSE_SESSION]:
        fn()

  def get(self, url: str) -> str:
    return asyncio.run(self.async_get(url))

  def get_tokens(self) -> Any:
    if BEFORE_GET_TOKENS in self.listeners:
      for fn in self.listeners[BEFORE_GET_TOKENS]:
        fn()
    return self.tokens

  # TODO remove_listener
  def add_listener(self, event: str, fn: Callable[[Any], None]) -> None:
    if event not in self.listeners:
      self.listeners[event] = []
    self.listeners[event].append(fn)

  def create_form(self, form_data) -> aiohttp.FormData:
    form = aiohttp.FormData()
    for k, v in form_data.items():
      form.add_field(k, v)
    return form

  async def websockets(self, url: str, callback: Callable[[Any], bool]) -> Any:
    try:
      for k, v in WS_MOCK_LIST.items():
        if re.match(k, url):
          path = os.path.join(test_dir, 'unit/mock', WS_MOCK_LIST[k])
          ret = []
          with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
              endwatch, obj = callback(line)
              ret.append(obj)
              if endwatch:
                return ret
            return ret

      # No url matched
      print("POST", url)
      assert (False)
    except Exception as e:
      # session closed?
      return False
