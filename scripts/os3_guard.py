#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import os
import sys
import time
from pathlib import Path


def newest_receipt(pattern: str) -> str | None:
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=lambda p: os.path.getmtime(p))


def main() -> int:
    ap = argparse.ArgumentParser(description="OS3 guard to prevent accidental double-runs.")
    ap.add_argument("--window", type=int, default=120, help="Guard window in seconds (default: 120).")
    ap.add_argument("--force", action="store_true", help="Bypass the guard window.")
    ap.add_argument("--pattern", default="os3/receipts/*.txt", help="Receipt glob pattern.")
    args = ap.parse_args()

    newest = newest_receipt(args.pattern)
    if not newest:
        return 0

    mtime = os.path.getmtime(newest)
    age = int(time.time() - mtime)

    # display path normalized for cross-platform logs
    newest_disp = Path(newest).as_posix()

    if age < args.window and not args.force:
        remaining = args.window - age
        print(f"⚠️  Newest receipt is only {age}s old (guard {args.window}s): {newest_disp}")
        print(f"    Wait {remaining}s or re-run with --force.")
        return 9

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
