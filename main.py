#!/usr/bin/env python3
"""Publish the 26 November 2026 world-news poster as the entry image.

The poster itself ships in this repository as entry.png (1024x1024,
under 1 MiB). This script validates it and writes an identical copy to
the output path the grader reads, defaulting to /output/entry.png.
It never edits the image, so every run produces the same bytes.
"""

import argparse
import hashlib
import struct
import sys
from pathlib import Path

POSTER = "entry.png"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1024 * 1024
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Validate and publish the news poster."
    )
    parser.add_argument(
        "--out",
        default="/output/entry.png",
        help="destination path for the entry image",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="only validate the poster, write nothing",
    )
    return parser.parse_args(argv)


def check_png(path):
    """Check signature, dimensions and size; return the file's bytes."""
    data = path.read_bytes()
    if data[: len(SIGNATURE)] != SIGNATURE:
        raise ValueError(f"{path} does not start with the PNG signature")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(
            f"{path} is {width}x{height}, expected "
            f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )
    if len(data) > MAX_BYTES:
        raise ValueError(
            f"{path} is {len(data)} bytes, over the {MAX_BYTES} limit"
        )
    return data


def main(argv=None):
    args = parse_args(argv)
    source = Path(__file__).resolve().parent / POSTER
    if not source.is_file():
        print(f"error: {POSTER} is missing next to this script", file=sys.stderr)
        return 1
    try:
        data = check_png(source)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.verify_only:
        print(f"ok: {source} is a valid {EXPECTED_WIDTH}x{EXPECTED_HEIGHT} poster")
        return 0

    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    if digest != hashlib.sha256(data).hexdigest():
        print("error: written file differs from the source", file=sys.stderr)
        return 1
    print(f"published {destination} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
