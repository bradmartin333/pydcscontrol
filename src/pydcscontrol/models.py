from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Channel(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3


class Mode(IntEnum):
    OFF = 0
    CONTINUOUS = 1
    PULSED = 2
    GATED_CONTINUOUS = 3


class TriggerEdge(IntEnum):
    FALLING = 0
    RISING = 1


@dataclass(frozen=True)
class DeviceInfo:
    host: str
    idn: str


@dataclass(frozen=True)
class ProfileName:
    profile_id: int
    name: str
