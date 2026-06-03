import pytest

from pydcscontrol.exceptions import DCSProtocolError
from pydcscontrol.models import Mode
from pydcscontrol.protocol import (
    ensure_terminated,
    parse_channel_configs,
    parse_profile_names,
    validate_channel,
    validate_profile,
)


# ---------------------------------------------------------------------------
# ensure_terminated
# ---------------------------------------------------------------------------


def test_ensure_terminated_adds_semicolon() -> None:
    assert ensure_terminated("*IDN?") == "*IDN?;"


def test_ensure_terminated_keeps_semicolon() -> None:
    assert ensure_terminated("SET:MODE:CHANNEL1,1;") == "SET:MODE:CHANNEL1,1;"


def test_ensure_terminated_strips_surrounding_whitespace() -> None:
    assert ensure_terminated("  *IDN?  ") == "*IDN?;"


def test_ensure_terminated_empty_raises() -> None:
    with pytest.raises(DCSProtocolError, match="empty"):
        ensure_terminated("")


def test_ensure_terminated_whitespace_only_raises() -> None:
    with pytest.raises(DCSProtocolError, match="empty"):
        ensure_terminated("   ")


# ---------------------------------------------------------------------------
# validate_channel
# ---------------------------------------------------------------------------


def test_validate_channel_returns_value() -> None:
    assert validate_channel(1) == 1
    assert validate_channel(2) == 2
    assert validate_channel(3) == 3


def test_validate_channel_zero_raises() -> None:
    with pytest.raises(DCSProtocolError):
        validate_channel(0)


def test_validate_channel_four_raises() -> None:
    with pytest.raises(DCSProtocolError):
        validate_channel(4)


# ---------------------------------------------------------------------------
# validate_profile
# ---------------------------------------------------------------------------


def test_validate_profile_valid_bounds() -> None:
    assert validate_profile(0) == 0
    assert validate_profile(5) == 5


def test_validate_profile_negative_raises() -> None:
    with pytest.raises(DCSProtocolError):
        validate_profile(-1)


def test_validate_profile_too_large_raises() -> None:
    with pytest.raises(DCSProtocolError):
        validate_profile(6)


# ---------------------------------------------------------------------------
# parse_profile_names
# ---------------------------------------------------------------------------


def test_parse_profile_names() -> None:
    xml_payload = '<profiles><profile id="0" name="default" /><profile id="1" name="inspect" /></profiles>'
    parsed = parse_profile_names(xml_payload)
    assert len(parsed) == 2
    assert parsed[0].profile_id == 0
    assert parsed[0].name == "default"
    assert parsed[1].profile_id == 1
    assert parsed[1].name == "inspect"


def test_parse_profile_names_empty_xml() -> None:
    parsed = parse_profile_names("<profiles/>")
    assert parsed == []


def test_parse_profile_names_invalid_xml_raises() -> None:
    with pytest.raises(DCSProtocolError, match="invalid profile names XML"):
        parse_profile_names("not xml at all")


# ---------------------------------------------------------------------------
# parse_channel_configs
# ---------------------------------------------------------------------------

_CHANNEL_XML = (
    "<channels>"
    '<channel id="1" current="250" mode="1" trigger="0" pulseWidth="100" delay="50"'
    ' maxCont="500" maxStrobe="1000" minOff="0" minCur="10" input="1"/>'
    '<channel id="2" current="0" mode="0" trigger="0" pulseWidth="0" delay="0"'
    ' maxCont="400" maxStrobe="800" minOff="0" minCur="0" input="0"/>'
    "</channels>"
)


def test_parse_channel_configs_valid() -> None:
    configs = parse_channel_configs(_CHANNEL_XML)
    assert len(configs) == 2

    ch1 = configs[0]
    assert ch1.channel_id == 1
    assert ch1.current == 250
    assert ch1.mode == Mode.CONTINUOUS
    assert ch1.trigger == 0
    assert ch1.pulse_width == 100
    assert ch1.delay == 50
    assert ch1.max_cont == 500
    assert ch1.max_strobe == 1000
    assert ch1.min_cur == 10
    assert ch1.input_pin == 1

    ch2 = configs[1]
    assert ch2.channel_id == 2
    assert ch2.mode == Mode.OFF


def test_parse_channel_configs_empty_xml() -> None:
    configs = parse_channel_configs("<channels/>")
    assert configs == []


def test_parse_channel_configs_invalid_xml_raises() -> None:
    with pytest.raises(DCSProtocolError, match="invalid channel config XML"):
        parse_channel_configs("not xml")


def test_parse_channel_configs_bad_attribute_value_raises() -> None:
    xml = '<channels><channel id="1" current="bad" mode="1" trigger="0" pulseWidth="0" delay="0" maxCont="0" maxStrobe="0" minOff="0" minCur="0" input="0"/></channels>'
    with pytest.raises(DCSProtocolError, match="invalid data type"):
        parse_channel_configs(xml)


def test_parse_channel_configs_invalid_mode_value_raises() -> None:
    xml = '<channels><channel id="1" current="100" mode="99" trigger="0" pulseWidth="0" delay="0" maxCont="0" maxStrobe="0" minOff="0" minCur="0" input="0"/></channels>'
    with pytest.raises(DCSProtocolError, match="invalid data type"):
        parse_channel_configs(xml)
