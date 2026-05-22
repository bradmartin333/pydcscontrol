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

## Quick Start

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

## Integrating Into Existing Projects

1. Wrap controller calls in an app-level service so protocol details are isolated.
2. Keep host/port/timeout values in configuration.
3. Unit test your service by mocking `DCSController.command` rather than requiring live hardware.

```python
from pydcscontrol import DCSController, Mode


class LightingService:
    def __init__(self, host: str, tcp_port: int = 777) -> None:
        self._controller = DCSController(host, tcp_port=tcp_port)

    def arm_inspection(self) -> None:
        self._controller.set_mode(1, Mode.CONTINUOUS)
        self._controller.set_level(1, 400)
```

## Development

```bash
uv sync
uv run pytest
uv build
```

## Notes

- Commands are automatically semicolon-terminated if omitted.
- The library raises typed exceptions for network and protocol issues.
