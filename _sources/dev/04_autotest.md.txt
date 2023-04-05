# Auto Test

```bash
pytest -v test/unit
# config `tests/e2e/e2e_test_config.py` before run command
pytest -v test/e2e
```

## Coverage test

```bash
python -m pytest --cov-report html --cov=codeforces_core tests/
# or
python -m pytest --cov-report html --cov=codeforces_core tests/unit
# or
python -m pytest --cov-report html --cov=codeforces_core tests/e2e
```

the output is at `htmlcov`

## Static type test

```bash
mypy --ignore-missing-imports codeforces_core
```

## Static gen

```bash
stubgen codeforces_core
```
