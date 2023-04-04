import json
import aiohttp
import pytest

from ..helper.MockAioHttpHelper import BEFORE_ASYNC_POST, MockAioHttpHelper

# 原版
# open_session
# get_tokens
# task = create_websocket
# create_form
# async_post
# asyncio.wait(task)
# async_get result


# 新版
# open_session
#   (account)
#   - login
# get_tokens
# task = create_websocket
#   (submit)
#   - create_form
#   - async_post
# asyncio.wait(task)
#   (result)
#   - async_get result
# close_session
@pytest.mark.asyncio
async def test_submit():
  from codeforces_core.submit import async_submit
  from ..helper.MockAioHttpHelper import BEFORE_OPEN_SESSION
  mahh = MockAioHttpHelper()

  get_tokens_called = False

  def check_get_tokens() -> None:
    nonlocal get_tokens_called
    get_tokens_called = True

  mahh.add_listener(BEFORE_OPEN_SESSION, check_get_tokens)

  def check_async_post(url: str, data: aiohttp.formdata.FormData) -> None:
    assert (url == '/contest/1777/problem/F?csrf_token=mock_csrf')
    # TODO cover form data
    # print(data._fields)

  mahh.add_listener(BEFORE_ASYNC_POST, check_async_post)

  await mahh.open_session()
  submit_id, resp = await async_submit(http=mahh,
                                       contest_id='1777',
                                       level='F',
                                       filename='tests/unit/mock/main.cpp',
                                       lang_id='73')
  assert submit_id == '200627167'

  assert get_tokens_called


def test_transform_submission():
  from codeforces_core.submit import transform_submission

  # ---------------- from contest ws Start ----------------
  data = json.loads(
      r'{"id": 11, "channel": "s_d3dd4b58d7fa6daf07e56129caa438cdebe15779", "text": {"t": "s", "d": [5973095027388772356, 200625609, 1777, 1746206, "TESTS", null, "TESTING", 0, 4, 0, 0, 148217099, "215020", "04.04.2023 3:21:48", "04.04.2023 3:21:48", 2147483647, 73, 0]}}'
  )
  parsed_data = transform_submission(data)
  assert parsed_data.contest_id == 1777
  assert parsed_data.date1 == '04.04.2023 3:21:48'
  assert parsed_data.date2 == '04.04.2023 3:21:48'
  assert parsed_data.lang_id == 73
  assert parsed_data.mem == 0
  assert parsed_data.ms == 0
  assert parsed_data.msg == 'TESTING'
  assert parsed_data.passed == 0
  assert parsed_data.testcases == 4
  assert parsed_data.title == 'TESTS'
  assert parsed_data.source == data
  assert parsed_data.submit_id == 200625609

  data = json.loads(
      r'{"id": 13, "channel": "s_9f6eebdd8339164206c94f091a8c3c8ec9415798", "text": {"t": "s", "d": [5973095143352889425, 200625609, 1777, 1746206, "TESTS", null, "TESTING", 0, 81, 0, 0, 148217099, "215020", "04.04.2023 3:21:48", "04.04.2023 3:21:48", 2147483647, 73, 0]}}'
  )
  parsed_data = transform_submission(data)
  assert parsed_data.testcases == 81

  data = json.loads(
      r'{"id": 14, "channel": "s_d3dd4b58d7fa6daf07e56129caa438cdebe15779", "text": {"t": "s", "d": [5973095147647856726, 200625609, 1777, 1746206, "TESTS", null, "OK", 86, 86, 3150, 7884800, 148217099, "21220", "04.04.2023 3:21:48", "04.04.2023 3:21:48", 2147483647, 73, 0]}}'
  )
  parsed_data = transform_submission(data)
  assert parsed_data.mem == 7884800
  assert parsed_data.ms == 3150
  assert parsed_data.msg == 'OK'
  assert parsed_data.passed == 86
  assert parsed_data.testcases == 86

  # ---------------- from contest ws End ----------------

  # ---------------- from common ws Start ----------------
  data = {
      'id': 1,
      'channel': '34f1ec4b729022e4b48f8d24b65c857805a90469',
      'text': {
          't':
          's',
          'd': [
              5973356517882654806, 200631363, 1777, 1746206, 'TESTS', None, 'OK', 86, 86, 3198, 7884800, 148217099,
              '21220', '04.04.2023 5:57:08', '04.04.2023 5:57:08', 2147483647, 73, 0
          ]
      }
  }
  parsed_data = transform_submission(data)
  assert parsed_data.date1 == '04.04.2023 5:57:08'
  assert parsed_data.date2 == '04.04.2023 5:57:08'
  assert parsed_data.mem == 7884800
  assert parsed_data.ms == 3198
  assert parsed_data.msg == 'OK'
  assert parsed_data.passed == 86
  assert parsed_data.testcases == 86
  assert parsed_data.submit_id == 200631363
  # ---------------- from common ws End ----------------
