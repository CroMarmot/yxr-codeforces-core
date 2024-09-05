=======
Publish
=======


config `~/.pypirc` follow https://packaging.python.org/en/latest/specifications/pypirc/

.. code-block::

  rm -rf dist/
  hatch build
  twine check dist/*
  tar -ztvf ./dist/yxr_codeforces_core-*.tar.gz
  # upload to test server
  twine upload --repository testpypi dist/*
  pip install --index-url https://test.pypi.org/simple/ --no-deps yxr-codeforces-core==<VERSION>
  ...
  # upload
  twine upload dist/*
  # If you use a mirror of PIP, through designated official pypi to test whether the upload successfully
  pip install --index-url https://pypi.org/simple/ yxr-codeforces-core==<VERSION>