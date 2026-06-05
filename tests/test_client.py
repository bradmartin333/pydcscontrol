"""Unit tests for DCSController — all network I/O is mocked."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from pydcscontrol import DCSController, DCSControllerWarning, DCSSignalWarning
from pydcscontrol.exceptions import DCSNetworkError, DCSProtocolError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_conn(response: bytes) -> MagicMock:
    """Return a mock create_connection context manager that yields one response."""
    mock_sock = MagicMock()
    # Return a short response so _read_all exits after the first recv call.
    mock_sock.recv.return_value = response
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_sock
    mock_ctx.__exit__.return_value = False
    return mock_ctx


def _channel_xml(
    channel_id: int = 1,
    current: int = 100,
    mode: int = 1,
    max_cont: int = 500,
) -> bytes:
    return (
        f"<channels>"
        f'<channel id="{channel_id}" current="{current}" mode="{mode}" trigger="0"'
        f' pulseWidth="0" delay="0" maxCont="{max_cont}" maxStrobe="1000"'
        f' minOff="0" minCur="0" input="0"/>'
        f"</channels>"
    ).encode()


# ---------------------------------------------------------------------------
# DCSController.__init__
# ---------------------------------------------------------------------------


def test_init_defaults() -> None:
    ctrl = DCSController()
    assert ctrl.host == "192.168.0.1"
    assert ctrl.tcp_port == 777
    assert ctrl.timeout_seconds == 1.0


def test_init_custom_values() -> None:
    ctrl = DCSController("10.0.0.5", tcp_port=800, timeout_seconds=2.5)
    assert ctrl.host == "10.0.0.5"
    assert ctrl.tcp_port == 800
    assert ctrl.timeout_seconds == 2.5


# ---------------------------------------------------------------------------
# DCSController.command
# ---------------------------------------------------------------------------


def test_command_connects_to_correct_host_and_port() -> None:
    ctrl = DCSController("10.0.0.1")
    with patch(
        "pydcscontrol.client.socket.create_connection",
        return_value=_mock_conn(b"OK"),
    ) as mock_conn:
        ctrl.command("*IDN?")
    mock_conn.assert_called_once_with(("10.0.0.1", 777), timeout=1.0)


def test_command_returns_stripped_response() -> None:
    ctrl = DCSController("10.0.0.1")
    with patch(
        "pydcscontrol.client.socket.create_connection",
        return_value=_mock_conn(b"  MANUFACTURER,DCS  \r\n"),
    ):
        result = ctrl.command("*IDN?")
    assert result == "MANUFACTURER,DCS"


def test_command_auto_terminates_with_semicolon() -> None:
    ctrl = DCSController("10.0.0.1")
    mock_sock = MagicMock()
    mock_sock.recv.return_value = b"OK"
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_sock
    mock_ctx.__exit__.return_value = False
    with patch("pydcscontrol.client.socket.create_connection", return_value=mock_ctx):
        ctrl.command("*IDN?")
    mock_sock.sendall.assert_called_once_with(b"*IDN?;")


def test_command_raises_network_error_on_os_error() -> None:
    ctrl = DCSController("10.0.0.1")
    with patch(
        "pydcscontrol.client.socket.create_connection",
        side_effect=OSError("connection refused"),
    ):
        with pytest.raises(DCSNetworkError, match="10.0.0.1:777"):
            ctrl.command("*IDN?")


def test_command_raises_protocol_error_on_error_response() -> None:
    ctrl = DCSController("10.0.0.1")
    with patch(
        "pydcscontrol.client.socket.create_connection",
        return_value=_mock_conn(b"ERROR: unknown command"),
    ):
        with pytest.raises(DCSProtocolError, match="ERROR"):
            ctrl.command("BADCMD")


def test_command_error_case_insensitive() -> None:
    ctrl = DCSController("10.0.0.1")
    with patch(
        "pydcscontrol.client.socket.create_connection",
        return_value=_mock_conn(b"error: bad value"),
    ):
        with pytest.raises(DCSProtocolError):
            ctrl.command("SET:LEVEL:CHANNEL1,-1")


# ---------------------------------------------------------------------------
# Validation helpers called by command wrappers
# ---------------------------------------------------------------------------


def test_set_level_negative_milliamps_raises() -> None:
    ctrl = DCSController("10.0.0.1")
    with pytest.raises(DCSProtocolError, match="milliamps"):
        ctrl.set_level(1, -1)


def test_set_level_invalid_channel_raises() -> None:
    ctrl = DCSController("10.0.0.1")
    with pytest.raises(DCSProtocolError, match="channel"):
        ctrl.set_level(4, 100)


def test_set_width_us_negative_raises() -> None:
    ctrl = DCSController("10.0.0.1")
    with pytest.raises(DCSProtocolError, match="width_us"):
        ctrl.set_width_us(1, -5)


def test_set_delay_us_negative_raises() -> None:
    ctrl = DCSController("10.0.0.1")
    with pytest.raises(DCSProtocolError, match="delay_us"):
        ctrl.set_delay_us(1, -1)


def test_set_profile_name_blank_raises() -> None:
    ctrl = DCSController("10.0.0.1")
    with pytest.raises(DCSProtocolError, match="blank"):
        ctrl.set_profile_name("   ")


def test_set_static_ip_blank_raises() -> None:
    ctrl = DCSController("10.0.0.1")
    with pytest.raises(DCSProtocolError, match="blank"):
        ctrl.set_static_ip("")


# ---------------------------------------------------------------------------
# DCSController.easy_set
# ---------------------------------------------------------------------------

# easy_set issues 4 commands: set_mode, set_level, channel_configs_xml, disconnect


def test_easy_set_returns_true_when_current_matches() -> None:
    responses = [b"OK", b"OK", _channel_xml(current=100), b"OK"]
    mock_ctxs = [_mock_conn(r) for r in responses]
    with patch("pydcscontrol.client.socket.create_connection", side_effect=mock_ctxs):
        result = DCSController.easy_set(host="10.0.0.1", current=100)
    assert result is True


def test_easy_set_returns_false_when_current_does_not_match() -> None:
    # Device echoes back a different current than requested
    responses = [b"OK", b"OK", _channel_xml(current=50), b"OK"]
    mock_ctxs = [_mock_conn(r) for r in responses]
    with patch("pydcscontrol.client.socket.create_connection", side_effect=mock_ctxs):
        result = DCSController.easy_set(host="10.0.0.1", current=100)
    assert result is False


def test_easy_set_warns_when_current_exceeds_max_cont() -> None:
    # current=600 > maxCont=500 triggers DCSSignalWarning; current still matches
    responses = [b"OK", b"OK", _channel_xml(current=600, max_cont=500), b"OK"]
    mock_ctxs = [_mock_conn(r) for r in responses]
    with patch("pydcscontrol.client.socket.create_connection", side_effect=mock_ctxs):
        with pytest.warns(DCSSignalWarning, match="exceeds maximum"):
            result = DCSController.easy_set(host="10.0.0.1", current=600)
    assert result is True


def test_easy_set_warns_when_mode_readback_differs() -> None:
    # Device reports mode=0 (OFF) despite us setting CONTINUOUS
    responses = [b"OK", b"OK", _channel_xml(current=100, mode=0), b"OK"]
    mock_ctxs = [_mock_conn(r) for r in responses]
    with patch("pydcscontrol.client.socket.create_connection", side_effect=mock_ctxs):
        with pytest.warns(DCSControllerWarning, match="mode"):
            result = DCSController.easy_set(host="10.0.0.1", current=100)
    assert result is True


def test_easy_set_warns_when_channel_not_in_response() -> None:
    # Empty channel list — channel 1 not found
    empty_xml = b"<channels/>"
    responses = [b"OK", b"OK", empty_xml, b"OK"]
    mock_ctxs = [_mock_conn(r) for r in responses]
    with patch("pydcscontrol.client.socket.create_connection", side_effect=mock_ctxs):
        with pytest.warns(DCSControllerWarning, match="not found"):
            result = DCSController.easy_set(host="10.0.0.1", current=100)
    assert result is False


def test_easy_set_uses_specified_channel() -> None:
    xml = (
        b"<channels>"
        b'<channel id="1" current="0" mode="0" trigger="0" pulseWidth="0" delay="0"'
        b' maxCont="500" maxStrobe="1000" minOff="0" minCur="0" input="0"/>'
        b'<channel id="2" current="200" mode="1" trigger="0" pulseWidth="0" delay="0"'
        b' maxCont="500" maxStrobe="1000" minOff="0" minCur="0" input="0"/>'
        b"</channels>"
    )
    responses = [b"OK", b"OK", xml, b"OK"]
    mock_ctxs = [_mock_conn(r) for r in responses]
    with patch("pydcscontrol.client.socket.create_connection", side_effect=mock_ctxs):
        result = DCSController.easy_set(host="10.0.0.1", channel=2, current=200)
    assert result is True


def test_easy_set_propagates_network_error() -> None:
    with patch(
        "pydcscontrol.client.socket.create_connection",
        side_effect=OSError("unreachable"),
    ):
        with pytest.raises(DCSNetworkError):
            DCSController.easy_set(host="10.0.0.1", current=100)
