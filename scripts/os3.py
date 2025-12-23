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

# --- OS3 PATH GUARD ---
import sys as _sys
from pathlib import Path as _Path
_ROOT = _Path(__file__).resolve().parents[1]
if str(_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_ROOT))
# --- END PATH GUARD ---


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


def cmd_love_coefficient(root: Path, text: str, witness: bool, no_receipt: bool) -> int:
    script = root / "scripts" / "os3_love_coefficient.py"
    if not script.exists():
        print("Missing scripts/os3_love_coefficient.py")
        return 2

    cmd = [sys.executable, str(script), "--text", text]
    if witness:
        cmd.append("--witness")
    if no_receipt:
        cmd.append("--no-receipt")

    p = sh(cmd, cwd=root)
    return p.returncode

def cmd_libra_assess(root: Path, text: str, fmt: str, witness: bool, strict: bool) -> int:
    """Assess text for public readiness (GREEN/YELLOW/RED)."""
    import sys
    
    # Handle --stdin: read from stdin if flag is present
    if '--stdin' in sys.argv:
        text = sys.stdin.read()
    
    # If text is empty even after stdin, show error
    if not text:
        print("Error: No text provided. Use --text or --stdin.", file=sys.stderr)
        return 2
    
    try:
        from os3.libra import assess, witness_block, redact
    except ImportError as e:
        print(f"Libra module missing: {e}", file=sys.stderr)
        return 2

        print(f"DEBUG: About to call assess() with text: {repr(text[:50])}...", file=sys.stderr)
        print(f"DEBUG: Text length: {len(text)}", file=sys.stderr)
    result = assess(text)

    
    if fmt == "json":
        print(result.to_json())
    else:
        print(result.to_text())
    
    if witness:
        redacted = None
        if result.redaction_needed:
            redacted, _, _ = redact(text)
        print()
        print(witness_block(text, result, redacted=redacted))
    
    return result.exit_code(strict=strict)


def cmd_libra_redact(root: Path, text: str, fmt: str, out: Optional[str]) -> int:
    """Redact PII deterministically."""
    # Handle --stdin: read from stdin if flag is present
    if '--stdin' in sys.argv:
        text = sys.stdin.read()
    
    # If text is empty even after stdin, show error
    if not text:
        print("Error: No text provided. Use --text or --stdin.", file=sys.stderr)
        return 2
    
    try:
        from os3.libra import redact, sha256_text
    except ImportError as e:
        print(f"Libra module missing: {e}", file=sys.stderr)
        return 2
    
    redacted_text, changed, findings = redact(text)
    
    if fmt == "json":
        import json
        payload = {
            "changed": changed,
            "sha256_original": sha256_text(text),
            "sha256_redacted": sha256_text(redacted_text),
            "findings": [{"code": f.code, "message": f.message} for f in findings]
        }
        print(json.dumps(payload, indent=2))
    else:
        print(redacted_text)
    
    if out:
        (root / out).write_text(redacted_text, encoding="utf-8")
        print(f"Written to: {out}", file=sys.stderr)
    
    return 0


def cmd_libra_seal(root: Path, text: str, redact_flag: bool, strict: bool) -> int:
    """Produce a paste-ready Libra witness block."""
    # Handle --stdin
    if '--stdin' in sys.argv:
        text = sys.stdin.read()
    
    if not text:
        print("Error: No text provided. Use --text or --stdin.", file=sys.stderr)
        return 2
    
    try:
        from os3.libra import assess, witness_block, redact
    except ImportError as e:
        print(f"Libra module missing: {e}", file=sys.stderr)
        return 2
    
    result = assess(text)
    redacted = None
    if redact_flag:
        redacted, _, _ = redact(text)
    
    print(witness_block(text, result, redacted=redacted))
    return result.exit_code(strict=strict)



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
    p_love = sub.add_parser("love-coefficient", help="Compute love coefficient (lexicon-based, truth-attested).")
    p_love.add_argument("--text", required=True, help="Text to analyze")
    p_love.add_argument("--witness", action="store_true", help="Print truth boundary (to stderr)")
    p_love.add_argument("--no-receipt", action="store_true", help="Do not write a receipt file")

    # Libra commands
    p_libra = sub.add_parser("libra", help="Libra OS: balance checks for public readiness")
    libra_sub = p_libra.add_subparsers(dest="libra_cmd", required=True)
    
    # assess
    p_assess = libra_sub.add_parser("assess", help="Assess text for public readiness (GREEN/YELLOW/RED)")
    p_assess.add_argument("--text", help="Text to assess")
    p_assess.add_argument("--stdin", action="store_true", help="Read input from stdin")
    p_assess.add_argument("--format", choices=["text", "json"], default="text")
    p_assess.add_argument("--witness", action="store_true", help="Print a witness block")
    p_assess.add_argument("--strict", action="store_true", help="Return exit code 1 for YELLOW")
    p_redact = libra_sub.add_parser("redact", help="Redact PII deterministically")
    p_assess.set_defaults(func=cmd_libra_assess)
    p_redact.add_argument("--text", help="Text to redact")
    p_redact.add_argument("--stdin", action="store_true", help="Read input from stdin")
    p_redact.add_argument("--format", choices=["text", "json"], default="text")
    p_redact.add_argument("--out", help="Write redacted output to this file")
    p_seal = libra_sub.add_parser("seal", help="Produce a paste-ready Libra witness block")
    p_seal.add_argument("--text", help="Text to seal")
    p_seal.add_argument("--stdin", action="store_true", help="Read input from stdin")
    p_seal.add_argument("--redact", action="store_true", help="Include redacted_sha256 if redaction changes text")
    p_seal.add_argument("--format", choices=["text", "json"], default="text")
    p_seal.add_argument("--witness", action="store_true", help="Print a witness block")
    p_seal.add_argument("--strict", action="store_true", help="Return exit code 1 for YELLOW")
    p_seal.set_defaults(func=cmd_libra_seal)

    p_redact.set_defaults(func=cmd_libra_redact)

    # Parse and dispatch
    args = ap.parse_args()
    root = repo_root(Path.cwd())
    
    if args.cmd == "libra" and hasattr(args, 'func'):
        kwargs = {'root': root, 'text': args.text if hasattr(args, 'text') else ''}
        if args.libra_cmd == 'assess':
            kwargs.update({'fmt': args.format, 'witness': args.witness, 'strict': args.strict})
        elif args.libra_cmd == 'redact':
            kwargs.update({'fmt': args.format, 'out': args.out})
        elif args.libra_cmd == 'seal':
            kwargs.update({'redact_flag': args.redact, 'strict': args.strict})
        return args.func(**kwargs)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
