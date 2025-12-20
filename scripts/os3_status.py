#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


FILL_TOKENS = ("REPLACE_WITH", "FILL_ME", "TODO", "TBD")


def repo_root() -> Path:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        if out:
            return Path(out)
    except Exception:
        pass
    return Path.cwd()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mini_yaml_load(text: str) -> Dict[str, Any]:
    """
    Minimal YAML loader for simple key: value session files.
    Supports quoted strings. Ignores nested structures.
    """
    d: Dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if v.startswith(("'", '"')) and v.endswith(("'", '"')) and len(v) >= 2:
            v = v[1:-1]
        d[k] = v
    return d


def load_doc(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if yaml is not None and path.suffix in (".yaml", ".yml"):
        try:
            obj = yaml.safe_load(text)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return mini_yaml_load(text)
    return mini_yaml_load(text)


def is_anchor_session(session_path: Path, episode: str) -> bool:
    name = session_path.name.lower()
    ep = (episode or "").lower()
    return (".anchor.session." in name) or name.endswith(".anchor.session.yaml") or ep.endswith("_anchor")


def exists_file(root: Path, p: str) -> Optional[Path]:
    if not p:
        return None
    # Guard against "." which caused your PermissionError earlier
    if p.strip() == ".":
        return None
    cand = Path(p)
    if not cand.is_absolute():
        cand = (root / cand).resolve()
    return cand if cand.exists() else None


def attestations_have_fill_tokens(att_dir: Path) -> bool:
    if not att_dir.exists():
        return False
    for p in att_dir.glob("*.yaml"):
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if any(tok in t for tok in FILL_TOKENS):
            return True
    return False


def session_status(root: Path, session_file: Path) -> Dict[str, Any]:
    s = load_doc(session_file)
    episode = str(s.get("episode", ""))

    anchor = is_anchor_session(session_file, episode)

    psalm_path = str(s.get("psalm_path", ""))
    psalm_sha = str(s.get("psalm_sha256", "")).strip()

    attest_path = str(s.get("attestation_path", "")).strip()
    bundle_path = str(s.get("bundle_path", "")).strip()

    presence_ref = str(s.get("felt_note_ref", "")).strip()
    if not presence_ref:
        # also accept "presence_path" if someone uses it
        presence_ref = str(s.get("presence_path", "")).strip()

    notes: List[str] = []

    # Psalm
    psalm_file = exists_file(root, psalm_path)
    psalm_ok = psalm_file is not None
    if not psalm_ok:
        notes.append("psalm_path_missing")
    else:
        if psalm_sha:
            cur = sha256_file(psalm_file)
            if cur != psalm_sha:
                psalm_ok = False
                notes.append("psalm_sha256_mismatch")
        else:
            notes.append("psalm_sha256_missing")

    # Presence (required for both)
    presence_file = exists_file(root, presence_ref)
    presence_ok = presence_file is not None
    if not presence_ok:
        notes.append("presence_missing")

    # Attestation
    attest_file = exists_file(root, attest_path)
    if attest_file is None:
        if anchor:
            attest_ok = True
            notes.append("attest_optional_missing")
        else:
            attest_ok = False
            notes.append("attest_path_missing")
    else:
        attest_ok = True

    # Bundle
    bundle_file = exists_file(root, bundle_path)
    if bundle_file is None:
        if anchor:
            bundle_ok = True
            notes.append("bundle_optional_missing")
        else:
            bundle_ok = False
            notes.append("bundle_path_missing")
    else:
        bundle_ok = True

    return {
        "episode": episode,
        "session_file": str(session_file.relative_to(root)).replace("/", "\\"),
        "psalm_ok": psalm_ok,
        "attest_ok": attest_ok,
        "bundle_ok": bundle_ok,
        "presence_ok": presence_ok,
        "notes": notes,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=["json"], default="json")
    args = ap.parse_args()

    root = repo_root()

    psalms_dir = root / "psalms"
    att_dir = root / "covenant" / "attestations"
    bundles_dir = root / "covenant" / "bundles"
    sessions_dir = root / "os3" / "sessions"
    presence_dir = root / "os3" / "presence"

    sessions: List[Dict[str, Any]] = []
    if sessions_dir.exists():
        for sf in sorted(sessions_dir.glob("*.yaml")):
            sessions.append(session_status(root, sf))

    counts = {
        "psalms": len(list(psalms_dir.glob("*.md"))) if psalms_dir.exists() else 0,
        "attestations": len(list(att_dir.glob("*.yaml"))) if att_dir.exists() else 0,
        "bundles": len(list(bundles_dir.glob("*.yaml"))) if bundles_dir.exists() else 0,
        "sessions": len(sessions),
        "presence_notes": len(list(presence_dir.glob("*.md"))) if presence_dir.exists() else 0,
    }

    # Overall OK logic:
    # - every session must have psalm_ok and presence_ok
    # - non-anchor sessions must also have attest_ok and bundle_ok
    overall_ok = True
    for s in sessions:
        if not (s["psalm_ok"] and s["presence_ok"]):
            overall_ok = False
            break
        # If it’s not an anchor, missing attest/bundle should fail
        is_anchor = "anchor" in (s.get("session_file", "").lower())
        if not is_anchor and not (s["attest_ok"] and s["bundle_ok"]):
            overall_ok = False
            break

    out = {
        "tool": "os3_status",
        "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "repo_root": str(root),
        "counts": counts,
        "attestations_have_fill_tokens": attestations_have_fill_tokens(att_dir),
        "sessions": sessions,
        "ok": overall_ok,
    }

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
