from dataclasses import dataclass
from typing import Tuple
from codeforces_core.interfaces.AioHttpHelper import AioHttpHelperInterface
from random import choice
from lxml import html
from .constants import CF_HOST

default_login_url = CF_HOST + "/enter?back=%2F"


@dataclass
class LoginResult:
  html: str = ''
  csrf: str = ''
  ftaa: str = ''
  bfaa: str = ''
  uc: str = ''
  usmc: str = ''
  cc: str = ''
  pc: str = ''
  success: bool = False


def is_user_logged_in(html_data: str) -> bool:
  doc = html.fromstring(html_data)
  links = doc.xpath('.//div[@class="lang-chooser"]/div[not(@style)]/a[@href]')
  for m in links:
    if m.text.strip() in ["Register", "Enter"]:
      return False
  return True


@DeprecationWarning
def check_login(html_data: str) -> bool:
  doc = html.fromstring(html_data)
  captions = doc.xpath('.//div[@class="caption titled"]')
  for c in captions:
    titled = c.text.strip()
    if titled == 'Login into Codeforces':
      return False
  return True


def extract_channel(html_data) -> Tuple[str, str, str, str]:
  doc = html.fromstring(html_data)
  uc = doc.xpath('.//meta[@name="uc"]')
  uc = uc[0].get('content') if len(uc) > 0 else None
  usmc = doc.xpath('.//meta[@name="usmc"]')
  usmc = usmc[0].get('content') if len(usmc) > 0 else None
  cc = doc.xpath('.//meta[@name="cc"]')
  cc = cc[0].get('content') if len(cc) > 0 else None
  pc = doc.xpath('.//meta[@name="pc"]')
  pc = pc[0].get('content') if len(pc) > 0 else None
  return uc, usmc, cc, pc


async def async_login(http: AioHttpHelperInterface,
                      handle: str,
                      passwd: str,
                      login_url=default_login_url) -> LoginResult:
  """
    This method will use ``http`` for login request, and  :py:func:`is_user_logged_in()` for login check

    :param handle: Codeforces handle
    :param password: Codeforces password

    :returns: if it is successful post and logged

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.account import async_login
        from codeforces_core.httphelper import HttpHelper

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          result = await async_login(http=http, handle='<handle>', passwd='<password>')
          await http.close_session()
          assert(result.success)

        asyncio.run(demo())
  """
  html_data = await http.async_get(login_url)
  doc = html.fromstring(html_data)
  csrf_token = doc.xpath('.//span[@class="csrf-token"]')[0].get('data-csrf')
  assert len(csrf_token) == 32, "Invalid CSRF token"
  ftaa = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789') for x in range(18)])
  # bfaa : Fingerprint2.x64hash128
  bfaa = ''.join([choice('0123456789abcdef') for x in range(32)])
  login_data = {
      'csrf_token': csrf_token,
      'action': 'enter',
      'ftaa': ftaa,
      'bfaa': bfaa,
      'handleOrEmail': handle,
      'password': passwd,
      'remember': 'on',
  }
  html_data = await http.async_post(login_url, login_data)
  try:
    uc, usmc, cc, pc = extract_channel(html_data)
  except:
    uc, usmc, cc, pc = '', '', '', ''

  success = False
  # if check_login(result.html):
  if is_user_logged_in(html_data=html_data):
    http.update_tokens(csrf=csrf_token, ftaa=ftaa, bfaa=bfaa, uc=uc, usmc=usmc)
    success = True
  else:
    success = False

  return LoginResult(html=html_data,
                     csrf=csrf_token,
                     ftaa=ftaa,
                     bfaa=bfaa,
                     uc=uc,
                     usmc=usmc,
                     cc=cc,
                     pc=pc,
                     success=success)
