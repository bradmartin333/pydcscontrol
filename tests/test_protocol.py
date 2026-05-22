from pydcscontrol.protocol import ensure_terminated, parse_profile_names, validate_channel


def test_ensure_terminated_adds_semicolon() -> None:
    assert ensure_terminated("*IDN?") == "*IDN?;"


def test_ensure_terminated_keeps_semicolon() -> None:
    assert ensure_terminated("SET:MODE:CHANNEL1,1;") == "SET:MODE:CHANNEL1,1;"


def test_validate_channel() -> None:
    assert validate_channel(1) == 1


def test_parse_profile_names() -> None:
    xml_payload = '<profiles><profile id="0" name="default" /><profile id="1" name="inspect" /></profiles>'
    parsed = parse_profile_names(xml_payload)
    assert len(parsed) == 2
    assert parsed[0].profile_id == 0
    assert parsed[0].name == "default"
