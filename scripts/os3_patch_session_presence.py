#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--session", required=True, help="Path to .session.yaml")
    p.add_argument("--presence", required=True, help="Path to presence note .md")
    args = p.parse_args()

    session_path = Path(args.session)
    presence_path = Path(args.presence)

    if not session_path.exists():
        raise SystemExit(f"Session file not found: {session_path}")
    if not presence_path.exists():
        raise SystemExit(f"Presence note not found: {presence_path}")

    text = session_path.read_text(encoding="utf-8", errors="replace").splitlines()

    # If felt_note_ref already exists, replace it; else append it.
    out = []
    replaced = False
    for line in text:
        if line.strip().startswith("felt_note_ref:"):
            out.append(f'felt_note_ref: "{presence_path.as_posix()}"')
            replaced = True
        else:
            out.append(line)

    if not replaced:
        # keep it simple: add at end
        out.append(f'felt_note_ref: "{presence_path.as_posix()}"')

    session_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("Patched session:", session_path)
    print("Set felt_note_ref ->", presence_path.as_posix())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
