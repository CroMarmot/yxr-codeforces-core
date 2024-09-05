# POST

from enum import Enum
from typing import Union
from codeforces_core.constants import CF_HOST
from codeforces_core.interfaces.AioHttpHelper import AioHttpHelperInterface
from codeforces_core.kwargs import extract_common_kwargs
from codeforces_core.util import calc_tta


# 3.11 StrEnum
class RankEnum(str, Enum):
  NEWBIE = "newbie"
  PUPIL = "pupil"
  SPECIALIST = "specialist"
  EXPERT = "expert"
  CANDIDATE_MASTER = "candidate master"
  MASTER = "master"
  INTERNATIONAL_MASTER = "international master"
  GRANDMASTER = "grandmaster"
  INTERNATIONAL_GRANDMASTER = "international grandmaster"
  LEGENDARY_GRANDMASTER = "legendary grandmaster"

  def __str__(self) -> str:
    return self.value


# `|` in python3.10
async def async_settings_rank(http: AioHttpHelperInterface, rank: RankEnum, password: str, **kw) -> Union[bool, None]:
  """
    every new year, you can change your rank with magic

    :param rank: RankEnum 
    :param password: Codeforces password

    :returns: if it is successful post

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.account import async_login 
        from codeforces_core.settings import RankEnum, async_settings_rank
        from codeforces_core.httphelper import HttpHelper

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          password = '<password>'
          result = await async_login(http=http, handle='<handle>', password=password)
          assert(result.success)
          html_data = await async_settings_rank(http=http,rank=RankEnum.NEWBIE,password=password)
          print(html_data)
          await http.close_session()

        asyncio.run(demo())
    """
  # TODO fix cloudflare 403
  raise NotImplementedError
  logger = extract_common_kwargs(**kw).logger
  tokens = http.get_tokens()
  _39ce7 = http.get_cookie(CF_HOST, '39ce7')
  _tta = calc_tta(_39ce7)
  data = {
      "csrf_token": tokens['csrf'],
      "action": "change",
      "password": password,
      "rank": str(rank),
      "_tta": _tta,
  }
  import time
  time.sleep(1)
  # cloudflare?
  try:
    resp = await http.async_get("/settings/rank")
    logger.debug(resp)
  except Exception as e:
    logger.exception(e)
    return False
  time.sleep(1)
  try:
    # TODO fix cloudflare 403
    resp = await http.async_post("/settings/rank", data)
    # , headers= {
    #   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #   'Accept-Encoding':'gzip, deflate, br',
    #   'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
    #   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    #   'Origin': 'https://codeforces.com',
    #   'Referer': 'https://codeforces.com/settings/rank',
    # })
    logger.debug(resp)
  except Exception as e:
    logger.exception(e)
    return False
  return True
