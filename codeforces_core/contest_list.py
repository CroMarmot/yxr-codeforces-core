from dataclasses import dataclass
import json
import re
from typing import List
import bs4
from lxml import html
from lxml.etree import ElementBase
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from .interfaces.AioHttpHelper import AioHttpHelperInterface
from .kwargs import extract_common_kwargs
from .util import soup_find_bs4Tag, soup_findall, typedxpath


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
  start: int  # timestamp
  length: str
  participants: str
  upcoming: bool
  # only for upcoming
  registered: bool
  # ['D','1','2'], ['C']
  Div: List[str]


def parse_div(title: str) -> List[str]:
  r: List[str] = []
  if "Div." in title:
    r += ["D"]
    for i in range(1, 5):
      if re.compile("Div\\. ?" + str(i)).search(title):
        r += [str(i)]
  elif not "unrated" in title.lower():
    r += ["C"]
  return r


# 获取已经解决的 统计
async def async_solved_count(http: AioHttpHelperInterface, solved_path: str):
  solved_string = await http.async_post("/data/contests", {"action": "getSolvedProblemCountsByContest"}, csrf=True)
  solved_json = json.loads(solved_string)
  open(solved_path, "w").write(solved_string)
  return solved_json


# [day:]hour:minutes
def ddhhmm2seconds(length: str) -> int:
  s = length.split(":")
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


def parse_contest_list(el: bs4.Tag, upcoming: bool, **kw) -> List[ContestListItem]:
  logger = extract_common_kwargs(**kw).logger
  contests: List[ContestListItem] = []

  for c in soup_findall(el, "tr", {"data-contestid": True}):
    try:
      cid = int(c.attrs["data-contestid"])
      td = soup_findall(c, "td")
      title = td[0].text.lstrip().splitlines()[0]
      authors: List[CodeforcesUser] = [
          CodeforcesUser(
              class__=a.attrs["class"][1],
              profile=a.attrs["href"],
              title=a.attrs["title"],
              name=a.get_text().strip(),
          ) for a in soup_findall(td[1], "a")
      ]
      start_str = soup_findall(td[2], "span")[0].text
      start = int(datetime.strptime(str(start_str) + "+0300", "%b/%d/%Y %H:%M%z").timestamp())  # Russian + 3hours
      length = td[3].text.strip()
      participants = ""
      registered = False

      if upcoming:
        # Registration completed x17284
        # Register » x1521 Until closing 4 days
        # Before registration 3 days
        msg: str = re.sub("\\s+", " ", td[5].getText().strip())
        if msg.startswith("Registration completed"):  # 完成注册
          registered = True
        elif msg.startswith("Before registration"):  # Before registration 3 days 还未开放注册 注册人数
          registered = False
        elif msg.startswith("Register"):  # 开放注册
          registered = False

        if msg.startswith("Registration completed") or msg.startswith("Register"):  # 开放注册
          renshu = soup_findall(td[5], "a", class_="contestParticipantCountLinkMargin")
          if len(renshu) == 1:
            participants = renshu[0].get_text().strip().lstrip("x")
      else:  # 历史
        participants = re.sub("\\s+", " ", td[5].get_text().strip().lstrip("x"))

      contests.append(
          ContestListItem(
              id=cid,
              title=title,
              authors=authors,
              start=start,
              length=length,
              participants=participants,
              registered=registered,
              upcoming=upcoming,
              Div=parse_div(title),
          ))
    except Exception as e:
      logger.exception(e)
  return contests


def parse_contest_list_page(html_str: str, **kw) -> ContestList:
  logger = extract_common_kwargs(**kw).logger
  soup = BeautifulSoup(html_str, features="lxml")
  # doc = html.fromstring(html_str)
  # tables = typedxpath(doc, './/div[@class="datatable"]')
  tables = soup_findall(soup, "div", class_="datatable")
  upcoming = parse_contest_list(tables[0], upcoming=True)

  # count contests
  if len(soup_findall(tables[1], "tr", {"data-contestid": True})) == 0:
    logger.error("[!] Contest is running or countdown")
  else:
    history = parse_contest_list(tables[1], upcoming=False)

  if not history:
    logger.error("? list1 is empty")
    return ContestList(upcomming=upcoming, history=[])
  return ContestList(upcomming=upcoming, history=history)


# This function is to simulate web request, do not do the cache
async def async_contest_list(http: AioHttpHelperInterface, page: int = 1, **kw) -> ContestList:
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
  html_str = await http.async_get(f"/contests/page/{page}?complete=true")
  return parse_contest_list_page(html_str, **kw)
