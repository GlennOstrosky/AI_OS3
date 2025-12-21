#!/usr/bin/env python3
"""
OS3 Holy Mirror (read-only display)

Purpose:
  Run the existing OS3 Psalm witness and reflect the result as a simple "holy mirror" panel.
  This is a DISPLAY LAYER, not a required rail.

Uses:
  - python scripts/os3_psalm_of_rails.py  (already shipped)

Exit semantics:
  Mirrors the psalm script:
    0 = Selah / complete
    9 = BLOCKED / not yet (boundary)
    1 = ERROR
"""

from __future__ import annotations

import subprocess
import sys
from typing import Tuple


def run_psalm() -> Tuple[int, str]:
    p = subprocess.run(
        [sys.executable, "scripts/os3_psalm_of_rails.py"],
        text=True,
        capture_output=True,
    )
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    combined = out if out else ""
    if err:
        combined = (combined + ("\n\n" if combined else "") + "STDERR:\n" + err).strip()
    return p.returncode, combined


def box(title: str, body: str) -> str:
    lines = [ln.rstrip() for ln in body.splitlines()]
    width = max([len(title)] + [len(ln) for ln in lines] + [38])
    top = "╔" + "═" * (width + 2) + "╗"
    mid = "╠" + "═" * (width + 2) + "╣"
    bot = "╚" + "═" * (width + 2) + "╝"
    t = f"║ {title.ljust(width)} ║"
    b = "\n".join([f"║ {ln.ljust(width)} ║" for ln in lines]) if lines else f"║ {'':{width}} ║"
    return "\n".join([top, t, mid, b, bot])


def main() -> int:
    rc, output = run_psalm()

    if rc == 0:
        title = "REFLECTION OF WHOLENESS  ✅"
        footer = "Selah. Rails holding. You may rest."
    elif rc == 9:
        title = "REFLECTION OF WORK REMAINING  ⏳"
        footer = "Boundary honored. Not yet. Continue gently."
    else:
        title = "REFLECTION OF ERROR  ⚠️"
        footer = "Something broke. Fix the rail, then return."

    panel = box(title, output)
    print(panel)
    print(footer)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
