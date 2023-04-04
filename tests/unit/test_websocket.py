import asyncio
from typing import Any, Tuple
import pytest

from ..helper.MockAioHttpHelper import BEFORE_ASYNC_POST, MockAioHttpHelper


@pytest.mark.asyncio
async def test_websocket():
  from codeforces_core.websocket import create_contest_ws_task
  from ..helper.MockAioHttpHelper import BEFORE_OPEN_SESSION
  mahh = MockAioHttpHelper()

  get_tokens_called = False

  def check_get_tokens() -> None:
    nonlocal get_tokens_called
    get_tokens_called = True

  mahh.add_listener(BEFORE_OPEN_SESSION, check_get_tokens)

  def ws_checker(data) -> Tuple[bool, Any]:
    return False, data

  await mahh.open_session()
  task = create_contest_ws_task(http=mahh, contestid='1777', ws_handler=ws_checker)
  res = await task
  assert len(res) == 8
  assert res[
      0] == r'{"id":11,"channel":"s_d3dd4b58d7fa6daf07e56129caa438cdebe15779","text":"{\"t\":\"s\",\"d\":[5973095027388772356,200625609,1777,1746206,\"TESTS\",null,\"TESTING\",0,4,0,0,148217099,\"215020\",\"04.04.2023 3:21:48\",\"04.04.2023 3:21:48\",2147483647,73,0]}"}' + '\n'
  assert res[
      -1] == r'{"id":14,"channel":"s_9f6eebdd8339164206c94f091a8c3c8ec9415798","text":"{\"t\":\"s\",\"d\":[5973095147647856726,200625609,1777,1746206,\"TESTS\",null,\"OK\",86,86,3150,7884800,148217099,\"21220\",\"04.04.2023 3:21:48\",\"04.04.2023 3:21:48\",2147483647,73,0]}"}'

  assert get_tokens_called
