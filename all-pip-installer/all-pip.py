#!/usr/bin/env python3
"""Install a curated set of common third-party Python packages."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from typing import TextIO


PROFILE_PACKAGES: dict[str, tuple[str, ...]] = {
    "basic": ("requests", "colorama", "rich"),
    "web": ("requests", "beautifulsoup4"),
    "scraping": ("requests", "beautifulsoup4", "mechanize"),
    "terminal": ("colorama", "pyfiglet", "rich"),
    "all": (
        "beautifulsoup4",
        "colorama",
        "mechanize",
        "pyfiglet",
        "requests",
        "rich",
    ),
}

PACKAGE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def select_packages(profile: str, extra_packages: Sequence[str] = ()) -> tuple[str, ...]:
    """Return a validated, de-duplicated package list for a named profile."""
    if profile not in PROFILE_PACKAGES:
        raise ValueError(f"Unknown profile: {profile}")

    selected = list(PROFILE_PACKAGES[profile])
    for package in extra_packages:
        if not PACKAGE_NAME_PATTERN.fullmatch(package):
            raise ValueError(
                f"Invalid package name {package!r}. Use a plain PyPI package name "
                "without shell syntax, URLs, or version specifiers."
            )
        selected.append(package)

    return tuple(dict.fromkeys(selected))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Preview a curated Python package profile. Installation is opt-in "
            "and requires the --install flag."
        )
    )
    parser.add_argument(
        "--profile",
        choices=tuple(PROFILE_PACKAGES),
        default="basic",
        help="Package profile to use (default: basic).",
    )
    parser.add_argument(
        "--package",
        action="append",
        default=[],
        metavar="NAME",
        help="Add a plain PyPI package name; may be supplied more than once.",
    )
    parser.add_argument(
        "--list",
        dest="list_profiles",
        action="store_true",
        help="List available profiles and their packages, then exit.",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Run pip install after displaying the package list and confirming.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt (requires --install).",
    )
    return parser


def print_profiles(stream: TextIO) -> None:
    print("Available package profiles:", file=stream)
    for name, packages in PROFILE_PACKAGES.items():
        print(f"  {name:<10} {', '.join(packages)}", file=stream)


def main(
    argv: Sequence[str] | None = None,
    *,
    run: Callable[..., object] = subprocess.run,
    input_fn: Callable[[str], str] = input,
    output: TextIO | None = None,
) -> int:
    """Run the CLI; injected I/O functions make behavior straightforward to test."""
    stream = sys.stdout if output is None else output
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.yes and not args.install:
        parser.error("--yes can only be used together with --install.")

    if args.list_profiles:
        print_profiles(stream)
        return 0

    try:
        packages = select_packages(args.profile, args.package)
    except ValueError as exc:
        parser.error(str(exc))

    print(f"Python interpreter: {sys.executable}", file=stream)
    print(f"Selected packages ({len(packages)}): {', '.join(packages)}", file=stream)
    print(
        "Use a virtual environment when possible. This tool does not create one "
        "or change the selected interpreter.",
        file=stream,
    )

    if not args.install:
        print("Dry run only; no packages were installed. Add --install to continue.", file=stream)
        return 0

    if not args.yes:
        try:
            answer = input_fn("Install the packages shown above? [y/N] ")
        except EOFError:
            print("No confirmation received; installation cancelled.", file=stream)
            return 1

        if answer.strip().lower() not in {"y", "yes"}:
            print("Installation cancelled; no changes were made.", file=stream)
            return 0

    command = [sys.executable, "-m", "pip", "install", *packages]
    print(f"Running pip for {len(packages)} selected package(s)...", file=stream)

    try:
        result = run(command, check=False)
    except OSError as exc:
        print(f"Could not start pip: {exc}", file=stream)
        return 1

    return_code = getattr(result, "returncode", 1)
    if return_code == 0:
        print("Package installation completed.", file=stream)
        return 0

    print(f"pip exited with status {return_code}.", file=stream)
    return return_code if isinstance(return_code, int) and return_code > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
