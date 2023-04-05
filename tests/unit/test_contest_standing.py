import pytest

from codeforces_core.contest_standing import async_friends_standing, async_common_standing
from tests.helper.MockAioHttpHelper import MockAioHttpHelper

pytest_plugins = ('pytest_asyncio', )


@pytest.mark.asyncio
async def test_async_friends_standing():
  mahh = MockAioHttpHelper()

  result = await async_friends_standing(mahh, contest_id='1779')
  assert result.head == ['rank', 'who', 'score', 'hack', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
  assert len(result.rows) == 26
  item = result.rows[3]
  assert item.rank == '13'
  assert item.who == 'QAQAutoMaton'
  assert item.score == '9282'
  assert item.penalty == ''
  assert len(item.problems) == 8
  assert item.problems[0].id == 'A'
  assert item.problems[0].score == '496'
  assert item.problems[0].time == '00:03'

  assert item.problems[7].id == 'H'
  assert item.problems[7].score == '-2'
  assert item.problems[7].time == ''


@pytest.mark.asyncio
async def test_async_common_standing():
  mahh = MockAioHttpHelper()

  result = await async_common_standing(mahh, contest_id='1779', page='2')
  assert result.head == ['rank', 'who', 'score', 'hack', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
  assert len(result.rows) == 200
  item = result.rows[1]
  assert item.rank == '202'
  assert item.who == 'JavierN'
  assert item.score == '6306'
  assert item.penalty == ''
  assert len(item.problems) == 8
  assert item.problems[0].id == 'A'
  assert item.problems[0].score == '491'
  assert item.problems[0].time == '00:06'

  assert item.problems[7].id == 'H'
  assert item.problems[7].score == ''
  assert item.problems[7].time == ''
