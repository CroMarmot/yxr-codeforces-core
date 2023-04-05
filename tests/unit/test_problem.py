import pytest

from codeforces_core.problem import ParseProblemResult

from ..helper.MockAioHttpHelper import MockAioHttpHelper

pytest_plugins = ('pytest_asyncio', )


@pytest.mark.asyncio
async def test_async_fetch_problems():
  from codeforces_core.problem import async_fetch_problem
  mahh = MockAioHttpHelper()

  result = await async_fetch_problem(mahh, contest_id='1779', level='F')
  print(result)
  assert result.status == ParseProblemResult.Status.NOTVIS
  assert result.status == 'NOTVIS'
  assert result.title == "Xorcerer's Stones"
  assert len(result.test_cases) == 3

  assert result.test_cases[0].in_data == '2\n13 13\n1'
  assert result.test_cases[0].out_data == '1\n1'
  assert result.test_cases[1].in_data == '7\n5 2 8 3 4 1 31\n1 1 2 2 3 3'
  assert result.test_cases[1].out_data == '-1'

  # assert result.description == '' # TODO
  assert result.time_limit == '4 seconds'
  assert result.mem_limit == '512 megabytes'
  # assert result.url == '' # TODO
  # assert result.html == '' # TODO
  # assert result.file_path == '' # TODO
  # assert result.id == '' # TODO
  # assert result.oj == '' # TODO
