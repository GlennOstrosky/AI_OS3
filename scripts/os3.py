#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

def _force_utf8_stdio() -> None:
    # Prevent Windows cp1252 UnicodeEncodeError (emoji etc.)
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def sh(cmd: list[str], *, cwd: Optional[Path] = None, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=capture)

def repo_root(start: Path) -> Path:
    p = start.resolve()
    for _ in range(50):
        if (p / ".git").exists():
            return p
        if p.parent == p:
            return start.resolve()
        p = p.parent
    return start.resolve()

def latest_session_file(root: Path) -> Optional[Path]:
    d = root / "os3" / "sessions"
    if not d.exists():
        return None
    sessions = sorted(d.glob("*.session.yaml"))
    return sessions[-1] if sessions else None

def parse_simple_yaml_kv(text: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out

def cmd_status(root: Path, fmt: str) -> int:
    script = root / "scripts" / "os3_status.py"
    if not script.exists():
        print("Missing scripts/os3_status.py")
        return 2

    if fmt == "json":
        # Print JSON to stdout (so you can redirect to a file)
        p = sh([sys.executable, str(script), "--format", "json"], cwd=root, capture=True)
        sys.stdout.write(p.stdout)
        sys.stderr.write(p.stderr)
        return p.returncode
    else:
        p = sh([sys.executable, str(script)], cwd=root)
        return p.returncode

def cmd_verify(root: Path, session: Optional[str], latest: bool) -> int:
    script = root / "scripts" / "os3_verify_session.py"
    if not script.exists():
        print("Missing scripts/os3_verify_session.py")
        return 2

    sess_path: Optional[Path] = None
    if latest or not session:
        sess_path = latest_session_file(root)
    else:
        sess_path = (root / session).resolve()

    if not sess_path or not sess_path.exists():
        print("No session file found.")
        return 2

    p = sh([sys.executable, str(script), "--session", str(sess_path)], cwd=root)
    return p.returncode

def cmd_receipt(root: Path, session: Optional[str], latest: bool, tag: Optional[str]) -> int:
    sess_path: Optional[Path]
    if latest or not session:
        sess_path = latest_session_file(root)
    else:
        sess_path = (root / session).resolve()

    if not sess_path or not sess_path.exists():
        print("No session file found for receipt.")
        return 2

    sess_text = sess_path.read_text(encoding="utf-8", errors="replace")
    sess = parse_simple_yaml_kv(sess_text)

    episode = sess.get("episode", "unknown_episode")
    ledger_tag = sess.get("ledger_tag", "")
    git_commit = sess.get("git_commit", "")
    presence = sess.get("felt_note_ref", sess.get("presence_note_ref", ""))
    attest = sess.get("attestation_path", "")
    psalm = sess.get("psalm_path", "")
    bundle = sess.get("bundle_path", "")

    # Verify (capture output)
    verify_script = root / "scripts" / "os3_verify_session.py"
    verify_pass = "UNKNOWN"
    verify_out = ""
    if verify_script.exists():
        p = sh([sys.executable, str(verify_script), "--session", str(sess_path)], cwd=root, capture=True)
        verify_out = (p.stdout + p.stderr).strip()
        verify_pass = "PASS" if p.returncode == 0 else "FAIL"

    # Write receipt
    receipts_dir = root / "os3" / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out_path = receipts_dir / f"{episode}_{utc.replace(':','')}_receipt.txt"

    lines = []
    lines.append("OS3 RECEIPT")
    lines.append(f"UTC: {utc}")
    lines.append("")
    lines.append(f"CEREMONY: {episode}")
    lines.append(f"SESSION: {sess_path.as_posix()}")
    if ledger_tag:
        lines.append("LEDGER_TAG:")
        lines.append(ledger_tag)
    if git_commit:
        lines.append(f"GIT_COMMIT: {git_commit}")
    if psalm:
        lines.append(f"PSALM: {psalm}")
    if attest:
        lines.append(f"ATTEST: {attest}")
    if bundle:
        lines.append(f"BUNDLE: {bundle}")
    if presence:
        lines.append(f"PRESENCE: {presence}")
    lines.append("")
    lines.append(f"VERIFY: {verify_pass} (rehash psalm/attest)")

    if verify_out:
        lines.append("")
        lines.append("VERIFY_OUTPUT:")
        lines.append(verify_out)

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote receipt: {out_path}")

    # Optional tag (annotated)
    if tag:
        # Create tag if missing
        try:
            sh(["git", "rev-parse", "--verify", tag], cwd=root, capture=True)
            print(f"Tag exists: {tag}")
        except Exception:
            pass

        p = sh(["git", "tag", "-a", tag, "-m", f"OS3 receipt sealed: {episode}", "HEAD"], cwd=root, capture=True)
        if p.returncode != 0 and "already exists" not in (p.stderr or ""):
            sys.stderr.write(p.stderr)
        else:
            print(f"Tagged: {tag}")

    # Commit receipt (best effort; won't fail your day)
    sh(["git", "add", str(out_path)], cwd=root)
    sh(["git", "commit", "-m", f"OS3: write receipt ({episode})"], cwd=root)
    return 0

def main() -> int:
    _force_utf8_stdio()

    ap = argparse.ArgumentParser(prog="os3")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_status = sub.add_parser("status", help="Show OS3 status (table or json).")
    p_status.add_argument("--format", choices=["table", "json"], default="table")

    p_verify = sub.add_parser("verify", help="Verify a session (rehash + compare).")
    p_verify.add_argument("--session", help="Path to session yaml (relative to repo root).")
    p_verify.add_argument("--latest", action="store_true", help="Verify latest session automatically.")

    p_receipt = sub.add_parser("receipt", help="Write a fresh receipt into os3/receipts/.")
    p_receipt.add_argument("--session", help="Path to session yaml (relative to repo root).")
    p_receipt.add_argument("--latest", action="store_true", help="Use latest session automatically.")
    p_receipt.add_argument("--tag", help="Optional annotated git tag to create at HEAD.")

    args = ap.parse_args()
    root = repo_root(Path("."))

    if args.cmd == "status":
        return cmd_status(root, args.format)
    if args.cmd == "verify":
        return cmd_verify(root, args.session, args.latest)
    if args.cmd == "receipt":
        return cmd_receipt(root, args.session, args.latest, args.tag)

    return 2

if __name__ == "__main__":
    raise SystemExit(main())
