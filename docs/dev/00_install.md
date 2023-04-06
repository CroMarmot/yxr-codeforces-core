# Install

## Clone

```bash
git clone git@github.com:CroMarmot/yxr-codeforces-core.git
cd yxr-codeforces-core
```

## Setup venv

```bash
python3 -m venv venv
```

## Enable venv

```bash
. venv/bin/activate
```

## Install dependencies

```bash
pip3 install .
pip3 install .[dev]
```

## Build

```bash
python -m build
```

## .vscode config

```
  "files.watcherExclude": {
    ".pytest_cache/**": true,
    "tests/unit/mock/**": true,
  }
```
