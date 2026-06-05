from __future__ import annotations

import socket
import warnings

from .exceptions import (
    DCSControllerWarning,
    DCSNetworkError,
    DCSProtocolError,
    DCSSignalWarning,
)
from .models import Mode, ProfileName, TriggerEdge
from .protocol import (
    ensure_terminated,
    parse_channel_configs,
    parse_profile_names,
    validate_channel,
    validate_profile,
)


class DCSController:
    """TCP/UDP client for Advanced Illumination DCS controllers."""

    def __init__(
        self,
        host: str = "192.168.0.1",
        *,
        tcp_port: int = 777,
        timeout_seconds: float = 1.0,
    ) -> None:
        self.host = host
        self.tcp_port = tcp_port
        self.timeout_seconds = timeout_seconds

    def command(self, command: str) -> str:
        """Send a SCPI-like command over TCP and return raw response text."""
        payload = ensure_terminated(command).encode("ascii", errors="ignore")

        try:
            with socket.create_connection(
                (self.host, self.tcp_port), timeout=self.timeout_seconds
            ) as sock:
                sock.settimeout(self.timeout_seconds)
                sock.sendall(payload)
                response = _read_all(sock)
        except OSError as exc:
            raise DCSNetworkError(
                f"failed to communicate with {self.host}:{self.tcp_port}"
            ) from exc

        result = response.decode("ascii", errors="ignore").strip()
        upper = result.upper()
        if upper.startswith("ERROR"):
            raise DCSProtocolError(result)
        return result

    def identify(self) -> str:
        return self.command("*IDN?")

    def channel_configs_xml(self) -> str:
        return self.command("*CHANNEL:CONFIGS?")

    def profile_number(self) -> str:
        return self.command("*PROFILE:NUMBER?")

    def profile_names(self) -> list[ProfileName]:
        return parse_profile_names(self.command("*PROFILE:NAMES?"))

    def set_level(self, channel: int, milliamps: int) -> str:
        validate_channel(channel)
        if milliamps < 0:
            raise DCSProtocolError("milliamps must be >= 0")
        return self.command(f"SET:LEVEL:CHANNEL{channel},{milliamps}")

    def set_mode(self, channel: int, mode: Mode) -> str:
        validate_channel(channel)
        return self.command(f"SET:MODE:CHANNEL{channel},{int(mode)}")

    def set_trigger_edge(self, channel: int, edge: TriggerEdge) -> str:
        validate_channel(channel)
        return self.command(f"SET:TRIGGER:CHANNEL{channel},{int(edge)}")

    def set_width_us(self, channel: int, width_us: int) -> str:
        validate_channel(channel)
        if width_us < 0:
            raise DCSProtocolError("width_us must be >= 0")
        return self.command(f"SET:WIDTH:CHANNEL{channel},{width_us}")

    def set_delay_us(self, channel: int, delay_us: int) -> str:
        validate_channel(channel)
        if delay_us < 0:
            raise DCSProtocolError("delay_us must be >= 0")
        return self.command(f"SET:DELAY:CHANNEL{channel},{delay_us}")

    def map_trigger_input(self, channel: int, trigger_input: int) -> str:
        validate_channel(channel)
        validate_channel(trigger_input)
        return self.command(f"MAP:TRIGGER:CHANNEL{channel},{trigger_input}")

    def software_trigger(self, channel: int) -> str:
        validate_channel(channel)
        return self.command(f"TRIGGER:CHANNEL{channel}")

    def save_profile(self, profile_number: int) -> str:
        validate_profile(profile_number)
        return self.command(f"SAVE:PROFILE,{profile_number}")

    def load_profile(self) -> str:
        return self.command("LOAD:PROFILE")

    def set_profile_name(self, name: str) -> str:
        name = name.strip()
        if not name:
            raise DCSProtocolError("profile name cannot be blank")
        return self.command(f"SET:PROFILE:NAME,{name}")

    def set_static_ip(self, ip_address: str) -> str:
        ip_address = ip_address.strip()
        if not ip_address:
            raise DCSProtocolError("ip_address cannot be blank")
        return self.command(f"SET:STATIC:IP,{ip_address}")

    def set_web_config(self, enabled: bool) -> str:
        return self.command(f"SET:WEB:CONFIG,{1 if enabled else 0}")

    def disconnect(self) -> str:
        return self.command("DISCONNECT")

    @classmethod
    def easy_set(
        cls,
        *,
        host: str = "192.168.0.1",
        channels: list[int],
        current: int,
        timeout_seconds: float = 1.0,
    ) -> bool:
        # Set the channel to continuous mode and specified current
        instance = cls(host=host, timeout_seconds=timeout_seconds)

        for channel in channels:
            instance.set_mode(channel, Mode.CONTINUOUS)
            instance.set_level(channel, current)

        # Read back channel configs
        xml_payload = instance.channel_configs_xml()

        # Disconnect before parsing to avoid leaving the channel on if parsing fails or raises warnings
        instance.disconnect()

        # Parse configs and validate
        configs = parse_channel_configs(xml_payload)
        configs_by_channel = {config.channel_id: config for config in configs}
        all_channels_valid = True

        for channel in channels:
            config = configs_by_channel.get(channel)
            if config is None:
                warnings.warn(
                    f"Channel {channel} configuration not found in device response",
                    DCSControllerWarning,
                )
                all_channels_valid = False
                continue

            if config.mode != Mode.CONTINUOUS:
                warnings.warn(
                    f"Channel {channel} mode should be {Mode.CONTINUOUS}, but is {config.mode}",
                    DCSControllerWarning,
                )

            if current > config.max_cont:
                warnings.warn(
                    f"Channel {channel} current {current} mA exceeds maximum continuous rating of {config.max_cont} mA",
                    DCSSignalWarning,
                )

            if config.current != current:
                all_channels_valid = False

        return all_channels_valid

    @classmethod
    def turn_off(
        cls,
        *,
        host: str = "192.168.0.1",
        channels: list[int],
        timeout_seconds: float = 1.0,
    ) -> bool:
        # Set the channel to continuous mode and specified current
        instance = cls(host=host, timeout_seconds=timeout_seconds)
        for channel in channels:
            instance.set_mode(channel, Mode.OFF)

        # Read back channel configs
        xml_payload = instance.channel_configs_xml()

        # Disconnect before parsing to avoid leaving the channel on if parsing fails or raises warnings
        instance.disconnect()

        # Parse configs and validate
        configs = parse_channel_configs(xml_payload)
        configs_by_channel = {config.channel_id: config for config in configs}
        all_channels_valid = True

        for channel in channels:
            config = configs_by_channel.get(channel)
            if config is None:
                warnings.warn(
                    f"Channel {channel} configuration not found in device response",
                    DCSControllerWarning,
                )
                all_channels_valid = False
                continue

            if config.mode != Mode.OFF:
                warnings.warn(
                    f"Channel {channel} mode should be {Mode.OFF}, but is {config.mode}",
                    DCSControllerWarning,
                )
                all_channels_valid = False

        return all_channels_valid


def _read_all(sock: socket.socket) -> bytes:
    chunks: list[bytes] = []
    while True:
        try:
            block = sock.recv(4096)
        except socket.timeout:
            break
        if not block:
            break
        chunks.append(block)
        if len(block) < 4096:
            break
    return b"".join(chunks)
