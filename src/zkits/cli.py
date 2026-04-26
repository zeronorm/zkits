"""Command-line interface for zkits."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .env import check_env


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zkits",
        description="Utilities bundled with the zkits Python package.",
    )
    parser.add_argument("--version", action="version", version="zkits 0.1.1")

    subparsers = parser.add_subparsers(dest="command", required=True)

    check_env_parser = subparsers.add_parser(
        "check_env",
        help="Print Python runtime and platform information.",
    )
    check_env_parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON.",
    )
    check_env_parser.set_defaults(func=_check_env_command)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def _check_env_command(args: argparse.Namespace) -> int:
    info = check_env()
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    print("zkits environment")
    print(f"python_version: {info['python_version']}")
    print(f"python_executable: {info['python_executable']}")
    print(f"platform: {info['platform']}")
    print(f"implementation: {info['implementation']}")
    print(f"cwd: {info['cwd']}")
    return 0
