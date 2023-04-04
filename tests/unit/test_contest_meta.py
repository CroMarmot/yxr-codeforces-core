import pytest

from codeforces_core.contest_meta import async_contest_meta, E_STATUS
from tests.helper.MockAioHttpHelper import MockAioHttpHelper

pytest_plugins = ('pytest_asyncio', )


@pytest.mark.asyncio
async def test_async_contest_meta():
  mahh = MockAioHttpHelper()

  result = await async_contest_meta(mahh, contest_id='1779')
  print(result)
  assert result.id == '1779'
  assert result.url == '/contest/1779'
  assert result.title == 'Hello 2023'

  assert len(result.problems) == 8
  assert result.problems[0].id == 'A'
  assert result.problems[0].url == '/contest/1779/problem/A'
  assert result.problems[0].name == 'Hall of Fame'
  assert result.problems[0].passed == '21412'
  assert result.problems[0].status == E_STATUS.AC
  assert result.problems[0].time_limit_msec == 1000
  assert result.problems[0].memory_limit_kb == 256000
  assert result.problems[0].contest_id == '1779'

  assert result.problems[4].id == 'E'
  assert result.problems[4].url == '/contest/1779/problem/E'
  assert result.problems[4].name == "Anya's Simultaneous Exhibition"
  assert result.problems[4].passed == '1437'
  assert result.problems[4].status == E_STATUS.NOT_SUBMITTED
  assert result.problems[4].time_limit_msec == 1000
  assert result.problems[4].memory_limit_kb == 256000
  assert result.problems[4].contest_id == '1779'

  assert len(result.materials) == 2
  assert result.materials[1].text == 'Editorial for Hello 2023'
  assert result.materials[1].url == '/blog/entry/110629'