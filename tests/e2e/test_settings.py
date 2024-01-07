import asyncio
import pytest
import os
# src
from codeforces_core.httphelper import HttpHelper
from codeforces_core.settings import RankEnum, async_settings_rank
# test
from . import test_e2e_dir

E2E_CONFIG_FILE = os.path.join(test_e2e_dir, 'e2e_test_config.py')

pytest_plugins = ('pytest_asyncio', )


@pytest.mark.asyncio
async def test_e2e_settings_rank():
  from codeforces_core.account import async_login,is_user_logged_in
  if not os.path.exists(E2E_CONFIG_FILE):
    raise Exception('e2e config file [e2e_test_config.py] not found')

  from .e2e_test_config import handle, password

  # token_path = os.path.join(test_e2e_dir, '.temp/token')
  # cookie_jar_path = os.path.join(test_e2e_dir, '.temp/cookie_jar')
  # http = HttpHelper(token_path=token_path, cookie_jar_path=cookie_jar_path)
  http = HttpHelper(token_path='', cookie_jar_path='')
  await http.open_session()
  result = await async_login(http=http, handle=handle, password=password)
  assert(result.success)
  assert is_user_logged_in(result.html)
  html_data = await async_settings_rank(http=http,rank=RankEnum.NEWBIE,password=password)
  await http.close_session()
  assert False
