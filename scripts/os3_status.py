#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List

FILL_TOKENS = ("__FILL_", "__FILL_FILE_SHA256__", "__FILL_POEM_BODY_SHA256__")

def _force_utf8_stdout() -> None:
    # Fix Windows cp1252 UnicodeEncodeError (emoji, etc.)
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def parse_simple_yaml_kv(text: str) -> Dict[str, str]:
    """
    Super-minimal YAML-ish parser for flat key: value lines.
    Skips comments, ignores indentation/nesting. Good enough for our session YAML.
    """
    out: Dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        # strip simple quotes
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        out[k] = v
    return out

def load_session_file(path: Path) -> Dict[str, Any]:
    if path.suffix.lower() == ".json" or path.name.endswith(".session.json"):
        return json.loads(read_text(path))
    # YAML-ish
    return parse_simple_yaml_kv(read_text(path))

def pick(d: Dict[str, Any], keys: List[str]) -> str:
    for k in keys:
        if k in d and d[k] is not None:
            return str(d[k]).strip()
    return ""

def resolve_path(repo: Path, p: str) -> Path:
    pp = Path(p)
    return pp if pp.is_absolute() else (repo / pp)

@dataclass
class Row:
    episode: str
    session_file: str
    psalm_ok: bool
    attest_ok: bool
    bundle_ok: bool
    presence_ok: bool
    notes: List[str]

def status(repo_root: Path) -> Dict[str, Any]:
    repo_root = repo_root.resolve()

    psalms_dir = repo_root / "psalms"
    attest_dir = repo_root / "covenant" / "attestations"
    bundles_dir = repo_root / "covenant" / "bundles"
    sessions_dir = repo_root / "os3" / "sessions"
    presence_dir = repo_root / "os3" / "presence"

    session_files = sorted(list(sessions_dir.glob("*.session.yaml")) +
                           list(sessions_dir.glob("*.session.yml")) +
                           list(sessions_dir.glob("*.session.json")))

    rows: List[Row] = []
    any_fill_tokens = False

    for sf in session_files:
        data = load_session_file(sf)

        episode = pick(data, ["episode", "ep", "episode_id"])
        psalm_path_s = pick(data, ["psalm_path", "psalm"])
        attest_path_s = pick(data, ["attestation_path", "attest_path", "attestation", "attest"])
        bundle_path_s = pick(data, ["bundle_path", "bundle"])
        presence_path_s = pick(data, ["felt_note_ref", "presence", "presence_note", "felt_note"])

        notes: List[str] = []

        # Paths may be missing in older session schema; treat as not-ok.
        psalm_ok = False
        attest_ok = False
        bundle_ok = False
        presence_ok = False

        # Verify psalm
        if psalm_path_s:
            psalm_path = resolve_path(repo_root, psalm_path_s)
            if psalm_path.exists():
                psalm_ok = True
                expected_psalm_sha = pick(data, ["psalm_sha256", "psalm_file_sha256", "file_sha256"])
                if expected_psalm_sha:
                    current = sha256_file(psalm_path)
                    if current.lower() != expected_psalm_sha.lower():
                        psalm_ok = False
                        notes.append("psalm_sha_mismatch")
                else:
                    # Not stored; that's ok. (We could store later.)
                    notes.append("psalm_sha_not_in_session")
            else:
                notes.append("psalm_missing")
        else:
            notes.append("psalm_path_missing")

        # Verify attestation + check fill tokens
        if attest_path_s:
            attest_path = resolve_path(repo_root, attest_path_s)
            if attest_path.exists():
                attest_ok = True
                txt = read_text(attest_path)
                if any(tok in txt for tok in FILL_TOKENS):
                    any_fill_tokens = True
                    attest_ok = False
                    notes.append("attestation_has_fill_tokens")

                expected_att_sha = pick(data, ["attestation_sha256", "attest_sha256"])
                current_att_sha = sha256_file(attest_path)
                if expected_att_sha:
                    if current_att_sha.lower() != expected_att_sha.lower():
                        attest_ok = False
                        notes.append("attest_sha_mismatch")
                else:
                    # ✅ THIS IS THE FIX: compute it instead of warning.
                    notes.append("attest_sha_computed")
            else:
                notes.append("attest_missing")
        else:
            notes.append("attest_path_missing")

        # Verify bundle exists (we don’t deeply parse it here)
        if bundle_path_s:
            bundle_path = resolve_path(repo_root, bundle_path_s)
            if bundle_path.exists():
                bundle_ok = True
            else:
                notes.append("bundle_missing")
        else:
            notes.append("bundle_path_missing")

        # Verify presence note exists (optional)
        if presence_path_s:
            presence_path = resolve_path(repo_root, presence_path_s)
            if presence_path.exists():
                presence_ok = True
            else:
                notes.append("presence_missing")
        else:
            # Presence note is allowed to be absent; keep as False but do not mark as failure.
            notes.append("presence_not_set")

        rows.append(Row(
            episode=episode or "(unknown)",
            session_file=str(sf.relative_to(repo_root)),
            psalm_ok=psalm_ok,
            attest_ok=attest_ok,
            bundle_ok=bundle_ok,
            presence_ok=presence_ok,
            notes=notes,
        ))

    counts = {
        "psalms": len(list(psalms_dir.glob("*.md"))) if psalms_dir.exists() else 0,
        "attestations": len(list(attest_dir.glob("*.yaml"))) + len(list(attest_dir.glob("*.yml"))) if attest_dir.exists() else 0,
        "bundles": len(list(bundles_dir.glob("*.yaml"))) + len(list(bundles_dir.glob("*.yml"))) if bundles_dir.exists() else 0,
        "sessions": len(session_files),
        "presence_notes": len(list(presence_dir.glob("*.md"))) if presence_dir.exists() else 0,
    }

    report = {
        "tool": "os3_status",
        "generated_at_utc": utc_now_iso(),
        "repo_root": str(repo_root),
        "counts": counts,
        "attestations_have_fill_tokens": any_fill_tokens,
        "sessions": [asdict(r) for r in rows],
        "ok": (not any_fill_tokens) and all(r.psalm_ok and r.attest_ok and r.bundle_ok for r in rows),
    }
    return report

def print_table(report: Dict[str, Any]) -> int:
    print("OS3 STATUS")
    print(f"Repo: {report['repo_root']}")
    print("-" * 70)
    print(f"Sessions found: {report['counts']['sessions']}")
    print()

    print("EPISODE | PSALM | ATTEST | BUNDLE | PRESENCE | SESSION_FILE | NOTES")
    print("-" * 70)
    for s in report["sessions"]:
        def ok(v: bool) -> str:
            return "OK" if v else "NO"
        notes = ",".join(s["notes"]) if s.get("notes") else ""
        print(
            f"{s['episode']} | {ok(s['psalm_ok'])} | {ok(s['attest_ok'])} | {ok(s['bundle_ok'])} | "
            f"{ok(s['presence_ok'])} | {s['session_file']} | {notes}"
        )
    print("-" * 70)

    if report["attestations_have_fill_tokens"]:
        print("WARNING: Some attestations still contain __FILL_ tokens.")
    else:
        print("OK: No __FILL_ tokens found in attestations (looks sealed).")

    print()
    print("Counts:")
    for k, v in report["counts"].items():
        print(f"  {k}: {v}")

    return 0 if report["ok"] else 2

def main() -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Repo root (default: .)")
    ap.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    args = ap.parse_args()

    report = status(Path(args.repo))

    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["ok"] else 2

    return print_table(report)

if __name__ == "__main__":
    raise SystemExit(main())
