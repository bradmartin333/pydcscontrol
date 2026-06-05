"""Unit tests for pydcscontrol CLI — all network I/O is mocked."""

import sys
from unittest.mock import patch

from pydcscontrol import main


@patch("builtins.print")
@patch("pydcscontrol.main.DCSController.easy_set", return_value=True)
def test_easy_set_uses_positional_arguments(mock_easy_set, mock_print) -> None:
    with patch.object(sys, "argv", ["pydcscontrol", "10.0.0.5", "200", "2"]):
        main.easy_set()

    assert mock_easy_set.call_args.kwargs == {
        "host": "10.0.0.5",
        "current": 200,
        "channel": 2,
    }
    mock_print.assert_called_once_with("DCS channel 2 set to 200 mA successfully")


@patch("builtins.print")
@patch("pydcscontrol.main.DCSController.easy_set", return_value=True)
def test_easy_set_default_host_and_channel_with_current_only(
    mock_easy_set, mock_print
) -> None:
    with patch.object(sys, "argv", ["easy-set", "100"]):
        main.easy_set()

    assert mock_easy_set.call_args.kwargs == {
        "host": "192.168.0.1",
        "current": 100,
        "channel": 1,
    }
    mock_print.assert_called_once_with("DCS channel 1 set to 100 mA successfully")


@patch("builtins.print")
@patch("pydcscontrol.main.DCSController.turn_off", return_value=True)
def test_turn_off_uses_positional_arguments(mock_turn_off, mock_print) -> None:
    with patch.object(sys, "argv", ["pydcscontrol", "10.0.0.5", "2"]):
        main.turn_off()

    assert mock_turn_off.call_args.kwargs == {
        "host": "10.0.0.5",
        "channel": 2,
    }
    mock_print.assert_called_once_with("DCS channel 2 powered down successfully")
