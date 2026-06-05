## pydcscontrol ![PyPI - Version](https://img.shields.io/pypi/v/pydcscontrol)

Python client library for communicating with Advanced Illumination DCS light controllers over the Ethernet interface.

This package implements the controller's SCPI-like command protocol over TCP (default port 777).

Even though the DCS controller is super simple, it is nice to be able to pull in a package to one-liner the most common operations.

These common operation wrappers also do a validation of the current configurations for a sanity check.

## Usage

### Command line (Using [uv](https://docs.astral.sh/uv/getting-started/installation/))

Using the `easy-set` CLI script to set the current of a DCS channel to 100 mA:

```bash
uvx pydcscontrol easy-set --current 100
```

Using the `turn-off` CLI script to turn off DCS output:

```bash
uvx pydcscontrol turn-off
```

### Python script

Install the package:

```bash
uv add pydcscontrol
# or
pip install pydcscontrol
```

Using continous mode to set the current of a DCS channel to 100 mA:

```python
from pydcscontrol import DCSController

if DCSController().easy_set(current=100):
    print("DCS channel configured successfully")
else:
    print("DCS channel configuration failed")
```

Quickly turn DCS output off:

```python
from pydcscontrol import DCSController

if DCSController().off():
    print("DCS channel turned off successfully")
else:
    print("Failed to turn off DCS channel")
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
