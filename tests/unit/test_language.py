import pytest
from ..helper.MockAioHttpHelper import MockAioHttpHelper

pytest_plugins = ('pytest_asyncio', )


@pytest.mark.asyncio
async def test_async_fetch_problems():
  from codeforces_core.language import async_fetch_language
  mahh = MockAioHttpHelper()

  result = await async_fetch_language(mahh)
  assert len(result) == 54
  assert result[0].text == 'GNU GCC C11 5.1.0'
  assert result[0].value == '43'

  assert result[1].text == 'Clang++20 Diagnostics'
  assert result[1].value == '80'