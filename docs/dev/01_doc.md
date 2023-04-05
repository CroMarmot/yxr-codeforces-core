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
cd docs && make clean && cd .. && sphinx-apidoc -f -o docs/ . tests setup.py && cd docs && make html && cd ..
```

## rst Examples

https://docutils.sourceforge.io/docs/user/rst/quickstart.html

https://docutils.sourceforge.io/docs/user/rst/quickref.html

https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc

rst py function:

https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#directive-py-function