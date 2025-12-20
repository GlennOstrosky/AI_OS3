#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm_path(value: str | None) -> Path | None:
    if value is None:
        return None
    v = str(value).strip()
    if v in ("", ".", "./"):
        return None
    return Path(v)


def _mini_yaml_load(text: str) -> dict:
    """
    Minimal YAML loader for our session files.
    Supports:
      - top-level 'key: value' pairs
      - quoted strings
      - ignores comments (# ...) and blank lines
    Not a general YAML parser (by design).
    """
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "---":
            continue
        # key: value
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", line)
        if not m:
            continue
        k = m.group(1)
        v = m.group(2).strip()
        # strip inline comment
        if " #" in v:
            v = v.split(" #", 1)[0].strip()
        # remove quotes
        if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
            v = v[1:-1]
        out[k] = v
    return out


def load_doc(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    # Prefer YAML if file extension says YAML
    if path.suffix.lower() in (".yml", ".yaml"):
        if yaml is not None:
            return yaml.safe_load(text) or {}
        # fallback mini-yaml
        return _mini_yaml_load(text)

    # Otherwise JSON
    return json.loads(text)


def _ok(msg: str) -> None:
    print(f"OK:   {msg}")


def _warn(msg: str) -> None:
    print(f"WARN: {msg}")


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")


def verify_session(session_path: Path) -> int:
    if not session_path.exists():
        _fail(f"session not found -> {session_path}")
        return 1

    s = load_doc(session_path)

    psalm_path = _norm_path(s.get("psalm_path"))
    attest_path = _norm_path(s.get("attestation_path"))
    bundle_path = _norm_path(s.get("bundle_path"))
    presence_path = _norm_path(s.get("felt_note_ref"))

    exp_psalm = (s.get("psalm_sha256") or "").strip()
    exp_attest = (s.get("attestation_sha256") or "").strip()

    errors = 0

    # Psalm
    if psalm_path and psalm_path.is_file():
        _ok(f"psalm found   -> {psalm_path.as_posix()}")
        if exp_psalm:
            cur = sha256_file(psalm_path)
            if cur == exp_psalm:
                _ok("psalm_sha256 matches")
            else:
                _fail("psalm_sha256 MISMATCH")
                _fail(f"  expected: {exp_psalm}")
                _fail(f"  current:  {cur}")
                errors += 1
        else:
            _warn("psalm_sha256 missing in session (skipping hash compare)")
    else:
        _fail(f"psalm missing -> {psalm_path}")
        errors += 1

    # Attestation (optional)
    if attest_path is None:
        _warn("attest not provided (skipping)")
    elif attest_path.is_dir():
        _warn(f"attest path is a directory ({attest_path}); treating as not provided")
    elif attest_path.is_file():
        _ok(f"attest found  -> {attest_path.as_posix()}")
        if exp_attest:
            cur = sha256_file(attest_path)
            if cur == exp_attest:
                _ok("attestation_sha256 matches")
            else:
                _fail("attestation_sha256 MISMATCH")
                _fail(f"  expected: {exp_attest}")
                _fail(f"  current:  {cur}")
                errors += 1
        else:
            _warn("attestation_sha256 missing in session (skipping hash compare)")
    else:
        _warn(f"attest missing -> {attest_path} (skipping)")

    # Bundle (optional)
    if bundle_path is None:
        _warn("bundle not provided (skipping)")
    elif bundle_path.is_dir():
        _warn(f"bundle path is a directory ({bundle_path}); treating as not provided")
    elif bundle_path.exists():
        _ok(f"bundle found  -> {bundle_path.as_posix()}")
    else:
        _warn(f"bundle missing -> {bundle_path} (skipping)")

    # Presence (optional)
    if presence_path and presence_path.exists():
        _ok(f"presence found -> {presence_path.as_posix()}")
    else:
        _warn("presence missing (skipping)")

    if errors == 0:
        print("RESULT: PASS ✅")
        return 0

    print(f"RESULT: FAIL ❌  ({errors} error(s))")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True, help="Path to session.yaml")
    args = ap.parse_args()
    return verify_session(Path(args.session))


if __name__ == "__main__":
    raise SystemExit(main())
