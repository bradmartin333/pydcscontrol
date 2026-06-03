## pydcscontrol ![PyPI - Version](https://img.shields.io/pypi/v/pydcscontrol)

Python client library for communicating with Advanced Illumination DCS light controllers over the Ethernet interface.

This package implements the controller's SCPI-like command protocol over TCP (default port 777) and supports UDP discovery (default port 7777).

## Installation

```bash
uv add pydcscontrol
# or
pip install pydcscontrol
```

## Usage

```python
from pydcscontrol import DCSController

if DCSController().easy_set(current=100):
    print("DCS channel configured successfully")
else:
    print("DCS channel configuration failed")
```

## Development

```bash
uv sync
uv run ruff check
uv run ruff format .
uv run pytest
uv build
git tag -a vX.Y.Z -m vX.Y.Z
git push --tags
```

If a deployment fails

```bash
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
git tag -a vX.Y.Z -m vX.Y.Z
git push --tags
```
