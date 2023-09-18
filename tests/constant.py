import os

test_dir = os.path.dirname(os.path.realpath(__file__))


def mock_file(filename: str) -> str:
  return os.path.join(test_dir, 'unit/mock', filename)
