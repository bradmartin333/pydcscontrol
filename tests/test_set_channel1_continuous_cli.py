from __future__ import annotations

import argparse

from pydcscontrol import DCSController, Mode


def percent_to_pulsewidth_us(percent: float, *, min_us: int = 30, max_us: int = 65_000) -> int:
    """Scale 0-100% linearly into pulse width microseconds."""
    if percent < 0 or percent > 100:
        raise ValueError("percent must be in range 0..100")
    if min_us < 0 or max_us <= min_us:
        raise ValueError("invalid pulse width range")

    ratio = percent / 100.0
    return int(round(min_us + (max_us - min_us) * ratio))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Set DCS channel 1 to continuous mode and scale 0-100% to pulse width. "
            "Pulse width is still written even though continuous mode primarily uses current."
        )
    )
    parser.add_argument("--host", required=True, help="DCS controller IP or hostname")
    parser.add_argument("--percent", required=True, type=float, help="Percent in range 0..100")
    parser.add_argument("--min-us", type=int, default=30, help="Minimum pulse width in microseconds")
    parser.add_argument("--max-us", type=int, default=65_000, help="Maximum pulse width in microseconds")
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
    pulse_width_us = percent_to_pulsewidth_us(args.percent, min_us=args.min_us, max_us=args.max_us)

    if args.dry_run:
        print(f"host={args.host}")
        print("mode=CONTINUOUS (1)")
        print(f"scaled_percent={args.percent:.2f}")
        print(f"pulse_width_us={pulse_width_us}")
        return 0

    controller = DCSController(args.host, tcp_port=args.tcp_port, timeout_seconds=args.timeout)
    mode_response = controller.set_mode(1, Mode.CONTINUOUS)
    width_response = controller.set_width_us(1, pulse_width_us)

    print(f"mode_response={mode_response}")
    print(f"width_response={width_response}")
    print(f"pulse_width_us={pulse_width_us}")
    return 0


def test_percent_to_pulsewidth_bounds() -> None:
    assert percent_to_pulsewidth_us(0) == 30
    assert percent_to_pulsewidth_us(100) == 65_000


def test_percent_to_pulsewidth_midpoint() -> None:
    assert percent_to_pulsewidth_us(50) == 32_515


if __name__ == "__main__":
    raise SystemExit(main())
