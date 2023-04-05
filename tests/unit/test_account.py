import pytest
from ..helper.MockAioHttpHelper import MockAioHttpHelper


def test_is_user_logged_in():
  from codeforces_core.account import is_user_logged_in
  mahh = MockAioHttpHelper()

  html = mahh.get('logged-codeforces.com')
  assert (is_user_logged_in(html) == True)
  html = mahh.get('notlogged-codeforces.com')
  assert (is_user_logged_in(html) == False)


def test_extract_channel():
  from codeforces_core.account import extract_channel
  mahh = MockAioHttpHelper()
  html = mahh.get('logged-codeforces.com')
  uc, usmc, cc, pc = extract_channel(html)
  assert uc == 'qwer1234'
  assert usmc == 'abcd1234'
  assert cc == None
  assert pc == None


@pytest.mark.asyncio
async def test_async_login():
  from codeforces_core.account import async_login
  from ..helper.MockAioHttpHelper import BEFORE_ASYNC_GET, BEFORE_UPDATE_TOKENS, BEFORE_ASYNC_POST
  mahh = MockAioHttpHelper()

  def async_get_checker(url) -> None:
    assert url == '/enter?back=%2F'

  mahh.add_listener(BEFORE_ASYNC_GET, async_get_checker)

  def async_post_checker(url, post_data) -> None:
    assert url == '/enter?back=%2F'
    assert post_data['csrf_token'] == '1f6e9a1ae9fab8aeed525b0f8a19881b'
    assert post_data['action'] == 'enter'
    # assert ftaa is random
    assert 'ftaa' in post_data
    # assert bfaa is random
    assert 'bfaa' in post_data
    assert post_data['handleOrEmail'] == 'handle'
    assert post_data['password'] == 'password'
    assert post_data['remember'] == 'on'

  mahh.add_listener(BEFORE_ASYNC_POST, async_post_checker)

  def update_token_checker(csrf: str, ftaa: str, bfaa: str, uc: str, usmc: str) -> None:
    assert csrf == '1f6e9a1ae9fab8aeed525b0f8a19881b'
    # assert ftaa is random
    # assert bfaa is random
    assert uc == 'qwer1234'
    assert usmc == 'abcd1234'

  mahh.add_listener(BEFORE_UPDATE_TOKENS, update_token_checker)

  await async_login(http=mahh, handle='handle', password='password')
