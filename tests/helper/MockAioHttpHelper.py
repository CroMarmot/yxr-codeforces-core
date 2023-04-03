import asyncio
import os
import re
import aiohttp
from typing import Any, Callable, Dict

from codeforces_core.interfaces.AioHttpHelper import AioHttpHelperInterface
from ..constant import test_dir

# The key is regex str instead of str
GET_MOCK_LIST: Dict[str, str] = {
    'logged-codeforces\\.com': 'logged-codeforces.com.html',
    'notlogged-codeforces\\.com': 'notlogged-codeforces.com.html',
    'https://codeforces.com/enter\\?back=%2F': 'notlogged-codeforces.com.html',
}

# The key is regex str instead of str
POST_MOCK_LIST: Dict[str, str] = {
    'https://codeforces.com/enter\\?back=%2F': 'logged-codeforces.com.html',
}

# TODO use Annotation
BEFORE_UPDATE_TOKENS = 'before:update_tokens'
BEFORE_ASYNC_GET = 'before:async_get'
BEFORE_ASYNC_POST = 'before:async_post'


class MockAioHttpHelper(AioHttpHelperInterface):

  def __init__(self) -> None:
    super().__init__()
    self.test_checker = {}

  def create_form(form_data: Dict[str, Any]) -> aiohttp.FormData:
    assert (False)

  async def async_get(self, url: str) -> str:
    if BEFORE_ASYNC_GET in self.test_checker:
      for fn in self.test_checker[BEFORE_ASYNC_GET]:
        fn(url)

    for k, v in GET_MOCK_LIST.items():
      if re.match(k, url):
        path = os.path.join(test_dir, 'unit/mock', GET_MOCK_LIST[k])
        with open(path, 'r') as f:
          return f.read()
    # No url matched
    print(url)
    assert (False)

  async def async_post(self, url: str, post_data: Dict[str, Any]) -> str:
    if BEFORE_ASYNC_POST in self.test_checker:
      for fn in self.test_checker[BEFORE_ASYNC_POST]:
        fn(url, post_data)

    for k, v in POST_MOCK_LIST.items():
      if re.match(k, url):
        path = os.path.join(test_dir, 'unit/mock', POST_MOCK_LIST[k])
        with open(path, 'r') as f:
          return f.read()
    # No url matched
    print(url)
    assert (False)

  def update_tokens(self, csrf: str, ftaa: str, bfaa: str, uc: str, usmc: str) -> None:
    if BEFORE_UPDATE_TOKENS in self.test_checker:
      for fn in self.test_checker[BEFORE_UPDATE_TOKENS]:
        fn(csrf, ftaa, bfaa, uc, usmc)

  async def open_session(self) -> aiohttp.ClientSession:
    assert (False)

  async def close_session(self) -> None:
    assert (False)

  def get(self, url: str) -> str:
    return asyncio.run(self.async_get(url))

  # TODO remove_listener
  def add_listener(self, event: str, fn: Callable[[Any], None]) -> None:
    if event not in self.test_checker:
      self.test_checker[event] = []
    self.test_checker[event].append(fn)
