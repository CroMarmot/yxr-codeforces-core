from typing import List, cast
import bs4
from lxml import html
from lxml.etree import ElementBase
from lxml.html import HtmlElement


def pop_element(t):
  text = t.text
  t.getparent().remove(t)
  return text


def show_message(resp):
  doc = html.fromstring(resp)
  for lines in doc.xpath('.//script[@type="text/javascript" and not(@src)]'):
    for l in lines.text.splitlines():
      if l.find('Codeforces.showMessage("') != -1:
        return l.split('"')[1]


# for mypy type check
def soup_find_bs4Tag(soup: bs4.Tag, *args, **kwargs) -> bs4.Tag:
  result = soup.find(*args, **kwargs)
  assert isinstance(result, bs4.Tag)  # or cast
  return result


def soup_findall(soup: bs4.Tag, *args, **kwargs) -> List[bs4.Tag]:
  result = soup.find_all(*args, **kwargs)
  return cast(List[bs4.Tag], result)


def typedxpath(el: ElementBase, s: str) -> List[ElementBase]:
  return cast(List[ElementBase], el.xpath(s))


def calc_tta(_39ce7):
  n = len(_39ce7)
  c = 0
  _tta = 0
  while c < n:
    _tta = (_tta + (c + 1) * (c + 2) * ord(_39ce7[c])) % 1009
    if c % 3 == 0:
      _tta += 1
    if c % 2 == 0:
      _tta *= 2
    if c > 0:
      _tta -= ((ord(_39ce7[c // 2]) // 2)) * (_tta % 5)
    while _tta < 0:
      _tta += 1009
    while _tta >= 1009:
      _tta -= 1009
    c += 1
  return str(_tta)
