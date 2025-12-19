#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_session_kv(p: Path) -> dict:
    data = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k:
            data[k] = v
    return data

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True, help="Path to .session.yaml")
    args = ap.parse_args()

    sp = Path(args.session)
    if not sp.exists():
        print("FAIL: session not found:", sp)
        return 2

    s = load_session_kv(sp)

    psalm_path = Path(s.get("psalm_path", ""))
    attest_path = Path(s.get("attestation_path", ""))
    bundle_path = Path(s.get("bundle_path", ""))
    presence_path = Path(s.get("felt_note_ref", "")) if s.get("felt_note_ref") else None

    ok = True

    def check_path(label: str, p: Path | None) -> None:
        nonlocal ok
        if p is None:
            return
        if not p.exists():
            print(f"FAIL: {label} missing -> {p}")
            ok = False
        else:
            print(f"OK:   {label} found   -> {p}")

    check_path("psalm", psalm_path)
    check_path("attest", attest_path)
    check_path("bundle", bundle_path)
    check_path("presence", presence_path)

    if psalm_path.exists() and "psalm_sha256" in s:
        cur = sha256_file(psalm_path)
        exp = s["psalm_sha256"].lower()
        if cur.lower() == exp:
            print("OK:   psalm_sha256 matches")
        else:
            print("FAIL: psalm_sha256 mismatch")
            print("  expected:", exp)
            print("  current: ", cur)
            ok = False

    if attest_path.exists() and "attestation_sha256" in s:
        cur = sha256_file(attest_path)
        exp = s["attestation_sha256"].lower()
        if cur.lower() == exp:
            print("OK:   attestation_sha256 matches")
        else:
            print("FAIL: attestation_sha256 mismatch")
            print("  expected:", exp)
            print("  current: ", cur)
            ok = False

    print("RESULT:", "PASS ✅" if ok else "FAIL ❌")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
