import argparse

from pydcscontrol import DCSController


def easy_set():
    parser = argparse.ArgumentParser(description="Current level to set on DCS channel")
    parser.add_argument(
        "host",
        type=str,
        help="The IP address of the DCS controller (default: 192.168.0.1)",
        nargs="?",
        default="192.168.0.1",
    )
    parser.add_argument("current", type=int, help="The current level in milliamps.")
    parser.add_argument(
        "channel",
        type=int,
        nargs="?",
        default=1,
        help="The DCS channel to configure (default: 1)",
    )
    args = parser.parse_args()
    if DCSController().easy_set(
        host=args.host, current=args.current, channel=args.channel
    ):
        print("DCS channel configured successfully")
    else:
        print("DCS channel configuration failed")


def turn_off():
    parser = argparse.ArgumentParser(description="Turn off DCS channel")
    parser.add_argument(
        "host",
        type=str,
        help="The IP address of the DCS controller (default: 192.168.0.1)",
        nargs="?",
        default="192.168.0.1",
    )
    parser.add_argument(
        "channel",
        type=int,
        nargs="?",
        default=1,
        help="The DCS channel to turn off (default: 1)",
    )
    args = parser.parse_args()
    if DCSController().turn_off(host=args.host, channel=args.channel):
        print("DCS channel powered down successfully")
    else:
        print("DCS channel power down failed")
