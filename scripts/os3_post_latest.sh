#!/usr/bin/env bash
set -euo pipefail

# Repo-native "post latest witness" runner.
# - always runs from repo root
# - derives latest tag from os3/ledger.jsonl
# - emits council update post + copies to clipboard

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TAG="$(
python - <<'PY' 2>/dev/null || true
import json
from pathlib import Path

p = Path("os3/ledger.jsonl")
if not p.exists():
    raise SystemExit(2)

lines = p.read_text(encoding="utf-8").splitlines()
for raw in reversed(lines):
    raw = raw.strip()
    if not raw:
        continue
    try:
        obj = json.loads(raw)
    except Exception:
        continue
    tag = (obj.get("tag") or "").strip()
    if tag:
        print(tag)
        raise SystemExit(0)

raise SystemExit(2)
PY
)"

if [[ -z "${TAG}" || "${TAG}" == --* ]]; then
  echo "Error: could not derive latest tag from os3/ledger.jsonl (got: '${TAG}')" >&2
  exit 2
fi

exec ./scripts/os3_council_update_post.sh --tag "${TAG}" --copy
