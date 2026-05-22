from pydcscontrol import DCSController, Mode, TriggerEdge


def test_symbols_available() -> None:
    assert DCSController is not None
    assert Mode.CONTINUOUS == 1
    assert TriggerEdge.RISING == 1
