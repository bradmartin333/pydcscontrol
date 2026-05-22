from __future__ import annotations

import argparse

from pydcscontrol import DCSController, Mode


def percent_to_current_ma(percent: float, *, min_ma: int = 0, max_ma: int = 1_500) -> int:
    """Scale 0-100% linearly into continuous-mode current milliamps."""
    if percent < 0 or percent > 100:
        raise ValueError("percent must be in range 0..100")
    if min_ma < 0 or max_ma <= min_ma:
        raise ValueError("invalid current range")

    ratio = percent / 100.0
    return int(round(min_ma + (max_ma - min_ma) * ratio))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Set DCS channel 1 to continuous mode and scale 0-100% to current."
        )
    )
    parser.add_argument("--host", required=True, help="DCS controller IP or hostname")
    parser.add_argument("--percent", required=True, type=float, help="Percent in range 0..100")
    parser.add_argument("--min-ma", type=int, default=0, help="Minimum current in milliamps")
    parser.add_argument("--max-ma", type=int, default=1_500, help="Maximum current in milliamps")
    parser.add_argument("--tcp-port", type=int, default=777, help="Controller TCP port")
    parser.add_argument("--timeout", type=float, default=1.0, help="Socket timeout in seconds")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print commands without sending to controller",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    current_ma = percent_to_current_ma(args.percent, min_ma=args.min_ma, max_ma=args.max_ma)

    if args.dry_run:
        print(f"host={args.host}")
        print("mode=CONTINUOUS (1)")
        print(f"scaled_percent={args.percent:.2f}")
        print(f"current_ma={current_ma}")
        return 0

    controller = DCSController(args.host, tcp_port=args.tcp_port, timeout_seconds=args.timeout)
    mode_response = controller.set_mode(1, Mode.CONTINUOUS)
    level_response = controller.set_level(1, current_ma)

    print(f"mode_response={mode_response}")
    print(f"level_response={level_response}")
    print(f"current_ma={current_ma}")
    return 0


def test_percent_to_current_bounds() -> None:
    assert percent_to_current_ma(0) == 0
    assert percent_to_current_ma(100) == 1_500


def test_percent_to_current_midpoint() -> None:
    assert percent_to_current_ma(50) == 750


if __name__ == "__main__":
    raise SystemExit(main())
