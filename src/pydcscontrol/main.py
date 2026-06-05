import argparse

from pydcscontrol import DCSController


def easy_set():
    parser = argparse.ArgumentParser(
        description="Set a DCS channel to a specified current level"
    )
    parser.add_argument(
        "--host",
        type=str,
        help="The IP address of the DCS controller (default: 192.168.0.1)",
        default="192.168.0.1",
    )
    parser.add_argument("current", type=int, help="The current level in milliamps.")
    parser.add_argument(
        "--channels",
        type=int,
        nargs="+",
        default=[1, 2],
        help="The DCS channel(s) to configure (default: 1, 2)",
    )
    args = parser.parse_args()
    channels_text = ", ".join(str(channel) for channel in args.channels)
    if DCSController().easy_set(
        host=args.host, current=args.current, channels=args.channels
    ):
        print(
            f"DCS channel{'s' if len(args.channels) != 1 else ''} {channels_text} set to {args.current} mA successfully"
        )
    else:
        print(
            f"DCS channel{'s' if len(args.channels) != 1 else ''} {channels_text} configuration failed"
        )


def turn_off():
    parser = argparse.ArgumentParser(description="Turn off DCS channel")
    parser.add_argument(
        "--host",
        type=str,
        help="The IP address of the DCS controller (default: 192.168.0.1)",
        default="192.168.0.1",
    )
    parser.add_argument(
        "--channels",
        type=int,
        nargs="+",
        default=[1, 2],
        help="The DCS channel(s) to turn off (default: 1, 2)",
    )
    args = parser.parse_args()
    channels_text = ", ".join(str(channel) for channel in args.channels)
    if DCSController().turn_off(host=args.host, channels=args.channels):
        print(
            f"DCS channel{'s' if len(args.channels) != 1 else ''} {channels_text} turned off successfully"
        )
    else:
        print(
            f"Failed to turn off DCS channel{'s' if len(args.channels) != 1 else ''} {channels_text}"
        )
