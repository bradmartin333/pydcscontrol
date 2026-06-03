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
class ProfileName:
    profile_id: int
    name: str


@dataclass
class ChannelSettings:
    channel_id: int
    current: int
    mode: Mode
    trigger: int
    pulse_width: int
    delay: int
    max_cont: int
    max_strobe: int
    min_off: int
    min_cur: int
    input_pin: int
