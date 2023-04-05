from dataclasses import dataclass
import json
import logging
import re
from typing import List
from lxml import html
from datetime import datetime, timedelta

from codeforces_core.interfaces.AioHttpHelper import AioHttpHelperInterface

logger = logging.getLogger(__name__)


@dataclass
class CodeforcesUser:
  name: str
  title: str
  class__: str
  profile: str


@dataclass
class ContestListItem:
  id: int
  title: str
  authors: List[CodeforcesUser]
  start: int
  length: str
  participants: str
  upcoming: bool
  # only for upcoming
  registered: bool
  # ['D','1','2'], ['C']
  Div: List[str]


def parse_div(title: str) -> List[str]:
  r: List[str] = []
  if 'Div.' in title:
    r += ['D']
    for i in range(1, 5):
      if re.compile('Div\\. ?' + str(i)).search(title): r += [str(i)]
  elif not 'unrated' in title.lower():
    r += ['C']
  return r


# 获取已经解决的 统计
async def async_solved_count(http: AioHttpHelperInterface, solved_path: str):
  solved_string = await http.async_post("/data/contests", {'action': 'getSolvedProblemCountsByContest'}, csrf=True)
  solved_json = json.loads(solved_string)
  open(solved_path, 'w').write(solved_string)
  return solved_json


# [day:]hour:minutes
def ddhhmm2seconds(length: str) -> int:
  s = length.split(':')
  days = int(s[0]) if len(s) == 3 else 0
  hours = int(s[-2])
  minutes = int(s[-1])
  return int(timedelta(days=days, hours=hours, minutes=minutes).total_seconds())


def is_contest_running(item: ContestListItem) -> bool:
  start = item.start
  end = start + ddhhmm2seconds(item.length)
  now = int(datetime.now().timestamp())  # local time zone
  return now >= start and now < end


@dataclass
class ContestList:
  upcomming: List[ContestListItem]
  history: List[ContestListItem]


def parse_contest_list(raw_contests, upcoming: bool) -> List[ContestListItem]:
  contests: List[ContestListItem] = []

  for c in raw_contests.xpath('.//tr[@data-contestid]'):
    cid = int(c.get('data-contestid'))
    td = c.xpath('.//td')
    title = td[0].text.lstrip().splitlines()[0]
    authors: List[CodeforcesUser] = [
        CodeforcesUser(
            class__=a.get('class').split(' ')[1],
            profile=a.get('href'),
            title=a.get('title'),
            name=a.text,
        ) for a in td[1].xpath('.//a')
    ]
    start = td[2].xpath('.//span')[0].text
    start = int(datetime.strptime(start + "+0300", "%b/%d/%Y %H:%M%z").timestamp())  # Russian + 3hours
    length = td[3].text.strip()
    participants = ''
    registration = False

    if upcoming:
      msg = td[5].text_content().strip()
      if msg.startswith("Registration completed"):
        registration = True
      participants = re.sub('\\s+', ' ', msg.split('x')[-1])
    else:
      participants = re.sub('\\s+', ' ', td[5].text_content().strip().lstrip('x'))

    contests.append(
        ContestListItem(id=cid,
                        title=title,
                        authors=authors,
                        start=start,
                        length=length,
                        participants=participants,
                        registered=registration,
                        upcoming=upcoming,
                        Div=parse_div(title)))
  return contests


# This function is to simulate web request, do not do the cache
async def async_contest_list(http: AioHttpHelperInterface, page: int = 1) -> ContestList:
  """
    This method will use ``http`` for get contests page, you can both login or not login

    :param page: the page in url

    :returns: the result 

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.httphelper import HttpHelper
        from codeforces_core.contest_list import async_contest_list
        
        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          # you can login before get list
          result = await async_contest_list(http=http)
          for c in result.upcomming[:5]:
              print(c)
          for c in result.history[:5]:
              print(c)
          await http.close_session()
        
        asyncio.run(demo())
  """
  doc = html.fromstring(await http.async_get(f'/contests/page/{page}'))
  table = doc.xpath('.//div[@class="datatable"]')
  upcoming = parse_contest_list(table[0], upcoming=True)

  # count contests
  if len(table[1].xpath('.//tr[@data-contestid]')) == 0:
    logger.error("[!] Contest is running or countdown")
  else:
    history = parse_contest_list(table[1], upcoming=False)

  if not history:
    logger.error("? list1 is empty")
    return ContestList(upcomming=upcoming, history=[])
  return ContestList(upcomming=upcoming, history=history)