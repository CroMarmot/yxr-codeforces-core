import asyncio
import os

# test
from . import test_e2e_dir

E2E_CONFIG_FILE = os.path.join(test_e2e_dir, 'e2e_test_config.py')

pytest_plugins = ('pytest_asyncio', )


def test_submit():
  # check comments in submit
  pass
