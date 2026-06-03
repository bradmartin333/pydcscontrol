from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from .exceptions import DCSProtocolError
from .models import ChannelSettings, Mode, ProfileName


_SEMICOLON_RE = re.compile(r";\s*$")


def ensure_terminated(command: str) -> str:
    command = command.strip()
    if not command:
        raise DCSProtocolError("command cannot be empty")
    if _SEMICOLON_RE.search(command):
        return command
    return f"{command};"


def validate_channel(channel: int) -> int:
    if channel not in (1, 2, 3):
        raise DCSProtocolError("channel must be 1, 2, or 3")
    return channel


def validate_profile(profile_number: int) -> int:
    if profile_number < 0 or profile_number > 5:
        raise DCSProtocolError("profile number must be in range 0..5")
    return profile_number


def parse_profile_names(xml_payload: str) -> list[ProfileName]:
    try:
        root = ET.fromstring(xml_payload)
    except ET.ParseError as exc:
        raise DCSProtocolError("invalid profile names XML payload") from exc

    profiles: list[ProfileName] = []
    for element in root.findall(".//profile"):
        profile_id = int(element.attrib.get("id", "0"))
        name = element.attrib.get("name", "")
        profiles.append(ProfileName(profile_id=profile_id, name=name))
    return profiles


def parse_channel_configs(xml_payload: str) -> list[ChannelSettings]:
    try:
        root = ET.fromstring(xml_payload)
    except ET.ParseError as exc:
        raise DCSProtocolError("invalid channel config XML payload") from exc

    channels: list[ChannelSettings] = []

    for element in root.findall(".//channel"):
        try:
            config = ChannelSettings(
                channel_id=int(element.attrib.get("id", "0")),
                current=int(element.attrib.get("current", "0")),
                mode=Mode(int(element.attrib.get("mode", "0"))),
                trigger=int(element.attrib.get("trigger", "0")),
                pulse_width=int(element.attrib.get("pulseWidth", "0")),
                delay=int(element.attrib.get("delay", "0")),
                max_cont=int(element.attrib.get("maxCont", "0")),
                max_strobe=int(element.attrib.get("maxStrobe", "0")),
                min_off=int(element.attrib.get("minOff", "0")),
                min_cur=int(element.attrib.get("minCur", "0")),
                input_pin=int(element.attrib.get("input", "0")),
            )
            channels.append(config)
        except ValueError as exc:
            raise DCSProtocolError(
                "invalid data type in channel config attributes"
            ) from exc

    return channels
