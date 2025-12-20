#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

LEDGER_DEFAULT = os.path.join("os3", "ledger.jsonl")

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_ledger(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Ledger not found: {path}")
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {i} in {path}: {e}") from e
    return rows

def pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)

def pick_target(rows: List[Dict[str, Any]], args: argparse.Namespace) -> Tuple[Optional[Dict[str, Any]], str]:
    if not rows:
        return None, "Ledger is empty."

    if args.last:
        return rows[-1], "Selected: last ledger entry."

    if args.line is not None:
        idx = args.line - 1
        if idx < 0 or idx >= len(rows):
            return None, f"--line {args.line} out of range (1..{len(rows)})."
        return rows[idx], f"Selected: ledger line {args.line}."

    if args.tag:
        matches = [r for r in rows if r.get("tag") == args.tag]
        if not matches:
            return None, f"No ledger rows found with tag={args.tag!r}."
        return matches[-1], f"Selected: most recent row with tag={args.tag!r}."

    if args.path:
        matches = [r for r in rows if r.get("path") == args.path]
        if not matches:
            return None, f"No ledger rows found with path={args.path!r}."
        return matches[-1], f"Selected: most recent row with path={args.path!r}."

    return None, "No selector provided. Use one of: --last | --line N | --tag TAG | --path PATH"

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify an OS3 receipt/snapshot file against os3/ledger.jsonl (expects hash field named 'sha256')."
    )
    ap.add_argument("--ledger", default=LEDGER_DEFAULT, help="Path to ledger JSONL (default: os3/ledger.jsonl)")
    sel = ap.add_mutually_exclusive_group(required=True)
    sel.add_argument("--last", action="store_true", help="Verify the last ledger entry")
    sel.add_argument("--line", type=int, help="Verify a specific ledger line number (1-based)")
    sel.add_argument("--tag", help="Verify the most recent ledger entry with this tag")
    sel.add_argument("--path", help="Verify the most recent ledger entry with this exact path")

    args = ap.parse_args()

    rows = read_ledger(args.ledger)
    row, why = pick_target(rows, args)
    if row is None:
        print(why, file=sys.stderr)
        return 2

    print("=== Ledger selection ===")
    print(why)
    print(pretty(row))

    snap_path = row.get("path")
    if not snap_path or not isinstance(snap_path, str):
        print("Ledger row missing valid 'path' field.", file=sys.stderr)
        return 3

    ledger_sha = row.get("sha256", "")
    if not ledger_sha or not isinstance(ledger_sha, str):
        print("Ledger row missing valid 'sha256' field (expected file hash).", file=sys.stderr)
        return 4

    if not os.path.exists(snap_path):
        print(f"Snapshot/receipt file not found: {snap_path}", file=sys.stderr)
        return 5

    file_sha = sha256_file(snap_path)

    print("\n=== File verification ===")
    try:
        st = os.stat(snap_path)
        mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
        print(f"path:        {snap_path}")
        print(f"size_bytes:  {st.st_size}")
        print(f"mtime_utc:   {mtime}")
    except Exception:
        print(f"path:        {snap_path}")

    print(f"file_sha256: {file_sha}")
    print(f"ledger_sha256:{ledger_sha}")

    if file_sha.lower() == ledger_sha.lower():
        print("\nMATCH ✅  (file hash equals ledger 'sha256')")
        return 0

    print("\nMISMATCH ❌  (file hash differs from ledger 'sha256')", file=sys.stderr)
    return 10

if __name__ == "__main__":
    raise SystemExit(main())
