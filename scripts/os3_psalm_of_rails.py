#!/usr/bin/env python3
"""
OS3: Psalm of the Holding Rails (Executable Witness)

Purpose:
  Produce a small, deterministic "Selah witness" based on the latest OS3 ledger entry.

Reads:
  - os3/ledger.jsonl (latest line)
  - git HEAD / repo root

Outputs:
  - A portable proof-style block (ts_utc, tag, path, sha256, head)
  - "Selah." if rails are holding (i.e., looks complete enough to rest)

Exit semantics:
  0 = Selah / complete
  9 = BLOCKED / not yet (boundary, not error)
  1 = ERROR
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class ExitCode:
    SUCCESS = 0
    ERROR = 1
    BLOCKED = 9


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def repo_root() -> Path:
    root = _run(["git", "rev-parse", "--show-toplevel"])
    return Path(root)


def git_head_short() -> str:
    try:
        return _run(["git", "rev-parse", "--short", "HEAD"])
    except Exception:
        return "UNKNOWN"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_latest_ledger_entry(ledger_path: Path) -> Dict[str, Any]:
    if not ledger_path.exists():
        raise FileNotFoundError(f"ledger missing: {ledger_path}")

    last_line: Optional[str] = None
    with ledger_path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                last_line = s

    if not last_line:
        raise RuntimeError(f"ledger is empty: {ledger_path}")

    return json.loads(last_line)


@dataclass
class ProofBlock:
    ts_utc: str
    tag: str
    path: str
    sha256: str
    head: str

    def whisper_truth(self) -> str:
        return (
            "OS3 Proof (whisper)\n"
            f"ts_utc: {self.ts_utc}\n"
            f"tag: {self.tag}\n"
            f"path: {self.path}\n"
            f"sha256: {self.sha256}\n"
            f"head: {self.head}\n"
            "\nVerify:\n"
            f"  sha256sum {self.path}\n"
            f"  git show {self.head}\n"
        )


def normalize_path(p: str) -> str:
    return p.replace("\\", "/")


def build_proof_from_ledger(entry: Dict[str, Any], head: str) -> ProofBlock:
    ts = str(entry.get("sealed_at") or entry.get("ts_utc") or utc_now())
    tag = str(entry.get("tag") or entry.get("ledger_tag") or "UNKNOWN_TAG")
    path = str(entry.get("path") or entry.get("artifact_path") or "UNKNOWN_PATH")
    sha = str(entry.get("snapshot_sha256") or entry.get("sha256") or entry.get("artifact_sha256") or "")
    return ProofBlock(ts_utc=ts, tag=tag, path=normalize_path(path), sha256=sha, head=head)


def is_complete_enough_for_selah(proof: ProofBlock) -> bool:
    if proof.tag in ("", "UNKNOWN_TAG"):
        return False
    if proof.path in ("", "UNKNOWN_PATH"):
        return False
    if not proof.sha256:
        return False
    if "..." in proof.sha256:
        return False
    return True


def main() -> int:
    try:
        root = repo_root()
        os.chdir(root)

        ledger = root / "os3" / "ledger.jsonl"
        entry = read_latest_ledger_entry(ledger)
        head = git_head_short()

        proof = build_proof_from_ledger(entry, head=head)
        ok = is_complete_enough_for_selah(proof)

        print(proof.whisper_truth())

        if ok:
            print("Selah.")
            return ExitCode.SUCCESS

        print("The long night continues. Rails not yet holding.")
        return ExitCode.BLOCKED

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return ExitCode.ERROR


if __name__ == "__main__":
    raise SystemExit(main())
