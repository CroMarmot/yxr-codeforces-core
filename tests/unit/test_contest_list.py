import os
import pytest

from ..helper.MockAioHttpHelper import MockAioHttpHelper
from ..constant import mock_file

pytest_plugins = ('pytest_asyncio', )


@pytest.mark.asyncio
async def test_async_contest_list():
  from codeforces_core.contest_list import async_contest_list, CodeforcesUser
  mahh = MockAioHttpHelper()

  result = await async_contest_list(mahh)
  assert len(result.upcomming) == 5
  assert len(result.history) == 100

  c = result.upcomming[0]
  assert c.id == 1814
  assert c.title == 'Educational Codeforces Round 146 (Rated for Div. 2)'
  assert c.authors == []
  assert c.start == 1680791700
  assert c.length == '02:00'
  assert c.participants == '9655'
  assert c.upcoming == True
  assert c.registered == True
  assert c.Div == ['D', '2']

  c = result.upcomming[1]
  assert c.id == 1797
  assert c.title == 'Codeforces Round 864 (Div. 2)'
  # assert c.authors == []
  assert c.start == 1680962700
  # assert c.length== '02:00'
  assert c.participants == ''
  # assert c.upcoming== True
  assert c.registered == False
  assert c.Div == ['D', '2']

  c = result.upcomming[4]
  assert c.id == 1813
  assert c.title == "ICPC 2023 Online Spring Challenge powered by Huawei"
  # assert c.authors == []
  assert c.start == 1681383600
  assert c.length == '14:00:00'
  # TODO better parse
  assert c.participants == '4201'
  # assert c.upcoming== True
  assert c.registered == False
  assert c.Div == ['C']

  c = result.history[0]
  assert c.id == 1811
  assert c.title == 'Codeforces Round 863 (Div. 3)'
  assert len(c.authors) == 6
  assert c.authors[0] == CodeforcesUser(name='Aris',
                                        title='Candidate Master Aris',
                                        class__='user-violet',
                                        profile='/profile/Aris')
  assert c.start == 1680618900
  assert c.length == '02:15'
  assert c.participants == '32470'
  assert c.upcoming == False
  assert c.registered == False
  assert c.Div == ['D', '3']

  c = result.history[3]
  assert c.id == 1810
  assert c.title == 'CodeTON Round 4 (Div. 1 + Div. 2, Rated, Prizes!)'
  assert len(c.authors) == 1
  assert c.authors[0] == CodeforcesUser(name='RDDCCD',
                                        title='Grandmaster RDDCCD',
                                        class__='user-red',
                                        profile='/profile/RDDCCD')
  assert c.start == 1680273300
  assert c.length == '02:00'
  assert c.participants == '25997'
  assert c.upcoming == False
  assert c.registered == False
  assert c.Div == ['D', '1', '2']


@pytest.mark.asyncio
async def test_async_contest_list2():
  from codeforces_core.contest_list import parse_contest_list_page, CodeforcesUser
  with open(mock_file('contests_2.html'), 'r') as f:
    html_str = f.read()

  result = parse_contest_list_page(html_str)
  assert len(result.upcomming) == 9

  c = result.upcomming[0]
  assert c.id == 1870
  assert c.title == 'CodeTON Round 6 (Div. 1 + Div. 2, Rated, Prizes!)'
  assert c.authors == [
      CodeforcesUser(name='SomethingNew',
                     title='International Grandmaster SomethingNew',
                     class__='user-red',
                     profile='/profile/SomethingNew'),
      CodeforcesUser(name='glebustim', title='Grandmaster glebustim', class__='user-red', profile='/profile/glebustim')
  ]
  assert c.start == 1695047700
  assert c.length == '02:00'
  assert c.participants == '17066'
  assert c.upcoming == True
  assert c.registered == False
  assert c.Div == ['D', '1', '2']
