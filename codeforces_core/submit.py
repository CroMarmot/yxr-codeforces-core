from collections import defaultdict
from dataclasses import dataclass, field
import logging
from os import path
from typing import Any, List, Tuple
from lxml import html

# from .ui import BLUE, GREEN, RED, redraw
from . import account
from .interfaces.AioHttpHelper import AioHttpHelperInterface

logger = logging.getLogger(__name__)


# return (contest_id, html_text of contest/<contest id>/my )
async def async_submit(http: AioHttpHelperInterface, contest_id: str, level: str, filename: str,
                       lang_id: str) -> Tuple[str, str]:
  """
    This method will use ``http`` to post submit

    :param http: AioHttpHelperInterface 
    :param ws_handler: function to handler messages 

    :returns: the task which run ws

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.httphelper import HttpHelper
        from codeforces_core.account import async_login
        from codeforces_core.websocket import create_contest_ws_task
        from codeforces_core.submit import async_submit, display_contest_ws

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          result = await async_login(http=http, handle='<handle>', password='<password>')
          assert(result.success)

          print('before submit')
          submit_id, resp = await async_submit(http, contest_id='1777', level='F', filename='F.cpp', lang_id='73')
          print('submit id:',submit_id)

          # connect websocket before submit sometimes cannot receive message
          contest_task = create_contest_ws_task(http, contest_id='1777', ws_handler=display_contest_ws)
          print("contest ws created");

          try:
            result = await asyncio.wait_for(contest_task, timeout=30)
            print("ws is done, result:", result)
          except asyncio.TimeoutError:
            pass
          await http.close_session()

        asyncio.run(demo())

  """

  if not contest_id or not level:
    logger.error("[!] Invalid contestID or level")
    return '', ''
  if not path.isfile(filename):
    logger.error("[!] File not found : {}".format(filename))
    return '', ''

  token = http.get_tokens()
  submit_form = {
      'csrf_token': token['csrf'],
      'ftaa': token['ftaa'],
      'bfaa': token['bfaa'],
      'action': 'submitSolutionFormSubmitted',
      'submittedProblemIndex': level,
      'programTypeId': lang_id,
  }
  url = '/contest/{}/problem/{}?csrf_token={}'.format(contest_id, level.upper(), token['csrf'])
  form = http.create_form(submit_form)
  form.add_field('sourceFile', open(filename, 'rb'), filename=filename)
  resp = await http.async_post(url, form)  # 正常是 302 -> https://codeforces.com/contest/<contest id>/my
  if not account.is_user_logged_in(resp):
    logger.error("Login required")
    return '', resp
  doc = html.fromstring(resp)
  for e in doc.xpath('.//span[@class="error for__sourceFile"]'):
    if e.text == 'You have submitted exactly the same code before':
      logger.error("[!] " + e.text)
      return '', resp

  status = parse_submit_status(resp)[0]
  assert status.url.split('/')[-1] == level.upper()
  return status.id, resp


# TODO move oiterminal code to here use dataclass
@dataclass
class SubmissionPageResult:
  id: str = ''
  url: str = ''
  verdict: str = ''
  time_ms: str = ''
  mem_bytes: str = ''


# status_url = f'/contest/{contest_id}/my'
# resp = await http.async_get(status_url)
# status = parse_submit_status(resp)
def parse_submit_status(html_page) -> List[SubmissionPageResult]:
  ret: List[SubmissionPageResult] = []
  doc = html.fromstring(html_page)
  tr = doc.xpath('.//table[@class="status-frame-datatable"]/tr[@data-submission-id]')
  for t in tr:
    td = t.xpath('.//td')
    submission_id = ''.join(td[0].itertext()).strip()
    url = td[3].xpath('.//a[@href]')[0].get('href')
    verdict = ''.join(td[5].itertext()).strip()
    prog_time = td[6].text.strip().replace('\xa0', ' ').split()[0]
    prog_mem = td[7].text.strip().replace('\xa0', ' ').split()[0]
    ret.append(SubmissionPageResult(id=submission_id, url=url, verdict=verdict, time_ms=prog_time, mem_bytes=prog_mem))
  return ret


@dataclass
class SubmissionWSResult:
  source: Any = field(default_factory=lambda: defaultdict(dict))
  submit_id: int = 0
  contest_id: int = 0
  title: str = ''
  msg: str = ''
  passed: int = 0
  testcases: int = 0
  ms: int = 0
  mem: int = 0
  date1: str = ''
  date2: str = ''
  lang_id: int = 0


# TODO 两个不同的ws(公共的和针对题目的) 似乎返回结构不同
def transform_submission(data: Any) -> SubmissionWSResult:
  d = data['text']['d']
  return SubmissionWSResult(
      source=data,
      # [5973095143352889425, ???? data-a
      submit_id=d[1],  # 200625609,
      contest_id=d[2],  # 1777,
      # 1746206, ??
      title=d[4],  # 'TESTS',
      # None,
      msg=d[6],  # 'TESTING', 'OK'
      passed=d[7],  # 0, ??
      testcases=d[8],  # 81, ?? 在测试过程中 这个值会增长,而d[7]一直是0,直到'OK'
      ms=d[9],  # 0,
      mem=d[10],  # 0, Bytes
      # 148217099,
      # '215020',
      date1=d[13],  # '04.04.2023 3:21:48',
      date2=d[14],  # '04.04.2023 3:21:48',
      # 2147483647,
      lang_id=d[16],  # 73,
      # 0]
  )


# return (end watch?, transform result)
def display_contest_ws(result: Any) -> Tuple[bool, Any]:
  parsed_data = transform_submission(result)
  print(parsed_data)
  if parsed_data.msg != 'TESTING':
    return True, parsed_data
  return False, parsed_data