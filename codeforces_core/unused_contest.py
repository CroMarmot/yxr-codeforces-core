#!/usr/bin/env python3
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import re
import asyncio
from typing import Any, List, Tuple
from lxml import html, etree

from codeforces_core.interfaces.AioHttpHelper import AioHttpHelperInterface
from . import util
# from . import _http
# from . import config
# from .ui import *
# from . import problem
from .constants import *
# from .config import conf, db
from time import time, sleep
from datetime import datetime, timezone, timedelta
from os import path, listdir, system, makedirs, sep
from sys import argv, exit
from operator import itemgetter

# async def async_view_submission(sid, lang, prefix=''):
#   extentions = {
#       'C++': 'cpp',
#       'Clang++': 'cpp',
#       'C11': 'c',
#       'Kotlin': 'kt',
#       'Java': 'java',
#       'Python': 'py',
#       'PyPy': 'py',
#       'C#': 'cs'
#   }
#   cache_dir = path.expanduser(conf['cache_dir']) + sep + prefix
#   makedirs(cache_dir, exist_ok=True)
#   json_path = cache_dir + sep + sid + '.json'
#   if path.isfile(json_path):
#     res = open(json_path, 'r').read()
#   else:
#     res = await _http.async_post("/data/submitSource", {'submissionId': sid})
#     open(json_path, 'w').write(res)
#   js = json.loads(res)
#   lang_ext = ''
#   for k, v in extentions.items():
#     if lang.find(k) != -1:
#       lang_ext = v
#       break
#   source_path = cache_dir + sep + sid + '.' + lang_ext
#   open(source_path, 'w').write(js['source'])
#   if "pager" in conf:
#     system(conf["pager"] + ' "' + source_path + '"')
#
#
# async def async_get_solutions(args):
#   cid, level = util.guess_cid(args)
#   if not cid or not level:
#     print("[!] Invalid contestID or level")
#     return
#   post_data = { 'action':'setupSubmissionFilter', \
#           'frameProblemIndex':level.upper(), \
#           'verdictName':'OK', \
#           'programTypeForInvoker':'anyProgramTypeForInvoker', \
#           'comparisonType':'NOT_USED', \
#           'judgedTestCount':'', \
#           'participantSubstring':'', \
#   }
#   order = 'BY_JUDGED_ASC'
#   await _http.open_session()
#   try:
#     for page in range(1, 20):
#       url = "/contest/{}/status/page/{}?order={}".format(cid, page, order)
#       res = await _http.async_post(url, post_data)
#       doc = html.fromstring(res)
#       rows = doc.xpath('.//table[@class="status-frame-datatable"]/tr[@data-submission-id]')
#       assert len(rows) > 0, "empty tr tag"
#       for tr in rows:
#         td = tr.xpath('.//td')
#         assert len(td) > 6, "not enough td tags"
#         sid = td[0].xpath('.//a[@class]')[0].text.strip()
#         when = datetime.strptime(
#             td[1].xpath('.//span')[0].text,
#             "%b/%d/%Y %H:%M").replace(tzinfo=config.tz_msk).astimezone(tz=None).strftime('%y-%m-%d %H:%M')
#         a = td[2].xpath('.//a[@href]')[0]
#         user = {}
#         if a.get('class'):
#           user['profile'] = a.get('href')
#           user['class'] = a.get('class').split(' ')[1]
#           c = user['class'].split('-')[1]
#         else:
#           user['class'] = ""  # Team
#           user['profile'] = ""
#           c = 'black'
#         user['title'] = a.get('title')
#         user['name'] = ''.join(a.itertext()).strip()
#         if c != 'black':
#           name = setcolor(c, user['name'].ljust(20))
#         else:
#           name = user['name'].ljust(20)
#         prob_title = td[3].xpath('.//a')[0].text.strip()
#         level = prob_title.split('-')[0].strip()
#         lang = td[4].text.strip()
#         verdict = td[5].xpath('.//span[@class="verdict-accepted"]')
#         verdict = verdict[0].text if verdict and verdict[0].text == 'Accepted' else None
#         if not verdict or verdict != 'Accepted': continue
#         ms = td[6].text.strip()
#         mem = td[7].text.strip()
#         print("{:9s} {} {:<15s} {:<20s} {:>7s} {:>8s} ".format(sid, name, prob_title, lang, ms, mem), end='')
#         choice = input("View? [Ynq] ").lower()
#         if choice in ["yes", 'y', '']:
#           r = await async_view_submission(sid, lang, str(cid) + level.lower())
#         elif choice in ["quit", 'q']:
#           return
#   finally:
#     await _http.close_session()
#
#
# async def async_get_contest_materials(args):
#   cid, _ = util.guess_cid(args)
#   contest_info = get_contest_info(cid)
#   if not cid or not contest_info:
#     print("[!] Invalid contestID")
#     return
#   await _http.open_session()
#   try:
#     contest_url = "/contest/{}".format(cid)
#     resp = await _http.async_get(contest_url)
#     doc = html.fromstring(resp)
#     captions = doc.xpath('.//div[@class="caption titled"]')
#     for c in captions:
#       title = c.text[1:].strip()
#       if title != 'Contest materials':
#         continue
#       links = c.getparent().xpath('.//a[@href]')
#       for a in links:
#         title_text = html.fromstring(a.get('title')).text_content()
#         print("[+] {}\n{}{}".format(title_text, CF_HOST, a.get('href')))
#   finally:
#     await _http.close_session()
#
#
# async def async_search_editorial(args):
#   cid, _ = util.guess_cid(args)
#   contest_info = get_contest_info(cid)
#   if not cid or not contest_info:
#     print("[!] Invalid contestID")
#     return
#   title = re.sub(r' ?\([^)]*\)', '', contest_info[0])
#   print("[+] Searching for", title, "editorial")
#   await _http.open_session()
#   try:
#     res = await _http.async_post('/search', {'query': title + ' editorial'})
#   finally:
#     await _http.close_session()
#   doc = html.fromstring(res)
#   topics = doc.xpath('.//div[@class="topic"]')
#   finding_words = [t.lower() for t in title.split()] + ['editorial']
#   if not topics:
#     print("[!] No result")
#     return
#   posts = []
#   for t in topics:
#     div = t.xpath('.//div[@class="title"]')
#     page_title = div.a.text.strip()
#     if page_title.lower().find('editorial') == -1: continue
#     page_url = CF_HOST + div.xpath('.//a')[0].get('href')
#     words = [t.lower() for t in page_title.split()]
#     matches = sum(w in finding_words for w in words)
#     posts += [{'title': page_title, 'url': page_url, 'match': matches}]
#
#   posts.sort(key=itemgetter('match'), reverse=True)
#   for p in posts:
#     print("\n[+] Title: {}\n[+] URL : {}".format(p['title'], p['url']))
#     if 'open_in_browser' in conf and conf['open_in_browser'] == True:
#       system('''{} "{}"'''.format(conf['browser'], p['url']))
#

# def get_solved_files():
#   ret = {}
#   for fn in listdir(path.expanduser(conf['solved_dir'])):
#     t = path.splitext(fn)
#     name = t[0]
#     ext = t[1].lstrip('.')
#     p = re.compile(r'^([0-9]+)([a-zA-Z])$').search(name)
#     if ext and ext in conf['lang_ext'] and p and len(p.groups()) == 2:
#       cid = int(p.group(1))
#       level = p.group(2)
#       if not cid in ret:
#         ret[cid] = [level]
#       else:
#         ret[cid].append(level)
#   return ret
