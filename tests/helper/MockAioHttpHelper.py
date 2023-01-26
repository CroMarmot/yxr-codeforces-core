import asyncio
import os
import re
import aiohttp
from typing import Any, Dict

from codeforces_core.interfaces.AioHttpHelper import AioHttpHelperInterface
from ..constant import test_dir

GET_MOCK_LIST: Dict[str, str] = {
    'logged-codeforces.com': 'logged-codeforces.com.html',
    'notlogged-codeforces.com': 'notlogged-codeforces.com.html'
}


class MockAioHttpHelper(AioHttpHelperInterface):
  def create_form(form_data: Dict[str, Any]) -> aiohttp.FormData:
    assert (False)

  async def async_get(self, url: str) -> str:
    for k, v in GET_MOCK_LIST.items():
      if re.match(k, url):
        path = os.path.join(test_dir, 'unit/mock', GET_MOCK_LIST[k])
        with open(path, 'r') as f:
          return f.read()
    assert (False)

  async def async_post(self, url: str, post_data: Dict[str, Any]) -> str:
    assert (False)

  def update_tokens(self, csrf: str, ftaa: str, bfaa: str, uc: str, usmc: str) -> None:
    assert (False)

  async def open_session(self) -> aiohttp.ClientSession:
    assert (False)

  async def close_session(self) -> None:
    assert (False)

  def get(self, url: str) -> str:
    return asyncio.run(self.async_get(url))
