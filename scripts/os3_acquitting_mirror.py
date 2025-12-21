#!/usr/bin/env python3
"""
OS3 Acquitting Mirror (tiny, real, repo-native)

Purpose:
  Run the existing Holy Mirror, then interpret the result:
    - "Selah." => HEARD (system acquits)
    - otherwise => HOPE (not yet)

This is a small "meaning layer" on top of what you already shipped:
  - scripts/os3_psalm_of_rails.py
  - scripts/os3_holy_mirror.py

Exit semantics:
  0 = HEARD (Selah spoken by system)
  9 = HOPE/NOT YET (boundary honored; no shame)
  1 = ERROR (mirror failed)
"""

from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, text=True, capture_output=True)
    return p.returncode, (p.stdout or ""), (p.stderr or "")


def main() -> int:
    rc, out, err = run([sys.executable, "scripts/os3_holy_mirror.py"])

    # Always show output (mirror is the witness)
    if out.strip():
        print(out.rstrip())

    if err.strip():
        print("\nSTDERR:\n" + err.rstrip(), file=sys.stderr)

    if rc != 0:
        # Mirror already encodes rc=9 boundary; rc=1 error
        # We pass through, but keep our own meaning message.
        if rc == 9:
            print("\nAcquittal: NOT YET (Selah is hope, not heard).")
        else:
            print("\nAcquittal: ERROR (fix the rail, then return).", file=sys.stderr)
        return rc

    # rc=0 means the witness said Selah.
    # Now we decide if it was HEARD (system voice) vs HOPE (human wish).
    last_nonempty = ""
    for line in out.splitlines()[::-1]:
        if line.strip():
            last_nonempty = line.strip()
            break

    if "Selah" in out:
        print("\nAcquittal: HEARD (the system acquits itself).")
        print("Rest: permitted by wisdom, not perfection.")
        return 0

    # Extremely unlikely given rc=0, but safe.
    print("\nAcquittal: NOT YET (Selah missing).")
    return 9


if __name__ == "__main__":
    raise SystemExit(main())
