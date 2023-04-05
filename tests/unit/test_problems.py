import pytest

from ..helper.MockAioHttpHelper import MockAioHttpHelper

pytest_plugins = ('pytest_asyncio', )


@pytest.mark.asyncio
async def test_async_fetch_problems():
  from codeforces_core.problems import async_fetch_problems
  mahh = MockAioHttpHelper()

  result = await async_fetch_problems(mahh, contest_id='1779')
  assert len(result) == 8

  A = result[0]
  assert A.title == 'A. Hall of Fame'
  assert A.level == 'A'
  assert A.time_limit_seconds == '1'
  assert A.memory_limit_mb == '256'

  E = result[4]
  assert E.title == "E. Anya's Simultaneous Exhibition"
  assert E.level == "E"
  assert len(E.in_tc) == 2
  assert len(E.out_tc) == 2

  F = result[5]
  assert F.in_tc[0] == '2\n13 13\n1'
  assert F.out_tc[0] == '1\n1'
  assert F.in_tc[1] == '7\n5 2 8 3 4 1 31\n1 1 2 2 3 3'
  assert F.out_tc[1] == '-1'
