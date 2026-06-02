## pydcscontrol

Python client library for communicating with Advanced Illumination DCS light controllers over the Ethernet interface.

This package implements the controller's SCPI-like command protocol over TCP (default port 777) and supports UDP discovery (default port 7777).

## Features

- Clean, typed Python API
- UDP device discovery
- Channel control helpers for mode, current, trigger edge, pulse width, and pulse delay
- Profile management helpers
- No native extension dependencies

## Installation

```bash
uv add pydcscontrol
# or
pip install pydcscontrol
```

## Usage

```python
from pydcscontrol import DCSController, Mode, TriggerEdge

controller = DCSController("192.168.1.40")

print(controller.identify())
controller.set_mode(1, Mode.CONTINUOUS)
controller.set_level(1, 250)
controller.set_trigger_edge(1, TriggerEdge.RISING)

devices = DCSController.discover(timeout_seconds=0.75)
for device in devices:
    print(device.host, device.idn)
```

## Development

```bash
uv sync
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

## Notes

- Commands are automatically semicolon-terminated if omitted.
- The library raises typed exceptions for network and protocol issues.
