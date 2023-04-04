from abc import abstractmethod
from typing import Any, Callable, Dict, Protocol, Tuple
import aiohttp
import json


class AioHttpHelperInterface(Protocol):

  @abstractmethod
  def create_form(form_data: Dict[str, Any]) -> aiohttp.FormData:
    raise NotImplementedError

  @abstractmethod
  async def async_get(url: str) -> str:
    raise NotImplementedError

  @abstractmethod
  async def async_post(url: str, post_data: Dict[str, Any]) -> str:
    raise NotImplementedError

  @abstractmethod
  def update_tokens(self, csrf: str, ftaa: str, bfaa: str, uc: str, usmc: str) -> None:
    raise NotImplementedError

  @abstractmethod
  async def open_session(self, cookie_jar_path: str, token_path: str) -> aiohttp.ClientSession:
    raise NotImplementedError

  @abstractmethod
  async def get_tokens(self) -> Any:
    raise NotImplementedError

  @abstractmethod
  async def close_session(self) -> None:
    raise NotImplementedError

  # TODO move call back out
  @abstractmethod
  async def websockets(self, url: str, callback: Callable[[Any], Tuple[bool, Any]]) -> Any:
    raise NotImplementedError
