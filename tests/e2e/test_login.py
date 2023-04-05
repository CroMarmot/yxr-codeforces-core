import pytest
import os
# src
from codeforces_core.httphelper import HttpHelper
# test
from . import test_e2e_dir

E2E_CONFIG_FILE = os.path.join(test_e2e_dir, 'e2e_test_config.py')

pytest_plugins = ('pytest_asyncio', )


@pytest.mark.asyncio
async def test_e2e_login():
  from codeforces_core.account import async_login
  if not os.path.exists(E2E_CONFIG_FILE):
    raise Exception('e2e config file [e2e_test_config.py] not found')

  from .e2e_test_config import handle, password

  # token_path = os.path.join(test_e2e_dir, '.temp/token')
  # cookie_jar_path = os.path.join(test_e2e_dir, '.temp/cookie_jar')
  # http = HttpHelper(token_path=token_path, cookie_jar_path=cookie_jar_path)
  http = HttpHelper(token_path='', cookie_jar_path='')
  await http.open_session()
  result = await async_login(http=http, handle=handle, password=password)
  await http.close_session()
  assert result.success


@pytest.mark.asyncio
async def test_e2e_login_failed():
  from codeforces_core.account import async_login
  # token_path = os.path.join(test_e2e_dir, '.temp/token')
  # cookie_jar_path = os.path.join(test_e2e_dir, '.temp/cookie_jar')
  # http = HttpHelper(token_path=token_path, cookie_jar_path=cookie_jar_path)
  http = HttpHelper(token_path='', cookie_jar_path='')
  await http.open_session()
  result = await async_login(http=http, handle='wrong handle', password='wrong password')
  await http.close_session()
  assert not result.success


@pytest.mark.asyncio
async def test_e2e_is_user_logged_in():
  from codeforces_core.account import is_user_logged_in, default_login_url

  # token_path = os.path.join(test_e2e_dir, '.temp/token')
  # cookie_jar_path = os.path.join(test_e2e_dir, '.temp/cookie_jar')
  # http = HttpHelper(token_path=token_path, cookie_jar_path=cookie_jar_path)
  http = HttpHelper(token_path='', cookie_jar_path='')
  await http.open_session()
  html = await http.async_get(default_login_url)
  await http.close_session()
  assert is_user_logged_in(html) == False
