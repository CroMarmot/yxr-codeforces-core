from . import unused_http
from . import config
from . import contest_meta
# from .ui import *
from .util import guess_contest_id, pop_element
from time import time, sleep
from os import listdir, path, sep, makedirs
from lxml import html, etree
# from .config import conf
import asyncio


def find_source_files(_dir):
  exts = [k['ext'] for k in conf['lang']]
  if not exts: return
  files = [_dir + sep + f for f in sorted(listdir(_dir)) if path.isfile(f) and path.splitext(f)[-1].lstrip('.') in exts]
  return files


def prepare_problem_dir(cid, level=None):
  p = path.expanduser(config.conf['contest_dir'] + sep + str(cid))
  if level == None:
    makedirs(p, exist_ok=True)
  else:
    p += sep + level.lower()
    makedirs(p, exist_ok=True)
  return p


def find_input_files(_dir):
  ins = sorted([
      _dir + sep + f for f in listdir(_dir) if path.isfile(f) and path.splitext(f)[-1] == '.txt' and f.startswith('in')
  ])
  return ins


def select_source_code(cid, level):
  prob_path = prepare_problem_dir(cid, level)
  files = find_source_files(prob_path)
  if len(files) == 0:
    return None
  elif len(files) >= 2:
    print("[!] There are multiple solutions")
    return None
  return files[0]


def generate_source(args):
  cid, level = guess_contest_id(args)
  if not cid or not level:
    print("[!] Invalid contestID or level")
    return
  template_path = path.expanduser(conf['template'])
  if not path.isfile(template_path):
    print("[!] Template file not found")
    return
  prob_dir = prepare_problem_dir(cid, level)
  ext = path.splitext(template_path)[-1]
  assert ext != "", "[!] File extension not found"
  new_path = prob_dir + sep + level.lower() + ext
  if path.exists(new_path):
    print("[!] File exists")
    return
  inf = open(template_path, 'r')
  outf = open(new_path, 'w')
  for line in inf:
    outf.write(line)
  print(GREEN('[+] Generate {}'.format(new_path)))
