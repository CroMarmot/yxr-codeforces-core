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
cd docs
sphinx-autobuild . ./_build/html/
```
