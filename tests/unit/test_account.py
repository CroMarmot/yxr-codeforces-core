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
