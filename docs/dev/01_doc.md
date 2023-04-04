# Doc

auto generate from code

```bash
sphinx-apidoc -f -o docs/ . tests setup.py
```

This will force overwriting

## Generate static html doc

```bash
cd docs
make html
```

The output file is at `./docs/_build/html/`

## Live doc

```bash
# This is hard to use, sometimes not refresh page
cd docs
sphinx-autobuild . ./_build/html/

# the better way
cd docs && make clean && cd .. && sphinx-apidoc -f -o docs/ . tests setup.py && cd docs && make html && cd ..
```
