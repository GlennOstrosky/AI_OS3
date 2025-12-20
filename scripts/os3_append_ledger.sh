#!/usr/bin/env bash
set -euo pipefail

# Append one JSONL ledger line for a receipt/snapshot + optional session + optional tag
# Usage:
#   ./scripts/os3_append_ledger.sh --path os3/receipts/FILE.txt [--tag TAG] [--session os3/sessions/FILE.yaml]
# Produces: os3/ledger.jsonl

PATH_ARG=""
TAG_ARG=""
SESSION_ARG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path) PATH_ARG="${2:-}"; shift 2 ;;
    --tag) TAG_ARG="${2:-}"; shift 2 ;;
    --session) SESSION_ARG="${2:-}"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 --path <file> [--tag <tag>] [--session <session.yaml>]"
      exit 0
      ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

: "${PATH_ARG:?Missing --path}"

mkdir -p os3
LEDGER="os3/ledger.jsonl"

UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
REPO="$(git rev-parse --show-toplevel)"
HEAD="$(git rev-parse HEAD)"

ABS_PATH="$PATH_ARG"
if [[ ! -f "$ABS_PATH" ]]; then
  echo "ERROR: file not found: $ABS_PATH" >&2
  exit 3
fi

FILE_SHA="$(sha256sum "$ABS_PATH" | awk '{print $1}')"

TAG_OBJECT=""
TAG_TARGET=""
if [[ -n "$TAG_ARG" ]]; then
  if git rev-parse --verify "$TAG_ARG" >/dev/null 2>&1; then
    TAG_OBJECT="$(git rev-parse "$TAG_ARG")"
    TAG_TARGET="$(git rev-parse "$TAG_ARG^{commit}")"
  else
    echo "WARN: tag not found: $TAG_ARG (skipping tag fields)" >&2
  fi
fi

SESSION_SHA=""
PSALM_SHA=""
if [[ -n "$SESSION_ARG" ]]; then
  if [[ -f "$SESSION_ARG" ]]; then
    SESSION_SHA="$(sha256sum "$SESSION_ARG" | awk '{print $1}')"
    # pull psalm_sha256 from YAML if present
    PSALM_SHA="$(grep -E '^psalm_sha256:' "$SESSION_ARG" | head -n 1 | sed -E 's/^psalm_sha256:[[:space:]]*//; s/"//g' || true)"
  else
    echo "WARN: session not found: $SESSION_ARG (skipping session fields)" >&2
  fi
fi

python - <<PY >> "$LEDGER"
import json
row = {
  "ts_utc": "$UTC",
  "repo": "$REPO",
  "head": "$HEAD",
  "path": "$ABS_PATH",
  "sha256": "$FILE_SHA",
}
if "$TAG_ARG":
  row["tag"] = "$TAG_ARG"
  if "$TAG_OBJECT": row["tag_object"] = "$TAG_OBJECT"
  if "$TAG_TARGET": row["target_commit"] = "$TAG_TARGET"
if "$SESSION_ARG":
  row["session"] = "$SESSION_ARG"
  if "$SESSION_SHA": row["session_sha256"] = "$SESSION_SHA"
  if "$PSALM_SHA": row["psalm_sha256"] = "$PSALM_SHA"
print(json.dumps(row, ensure_ascii=False))
PY

echo "Appended -> $LEDGER"
echo "path_sha256=$FILE_SHA"
if [[ -n "$PSALM_SHA" ]]; then
  echo "psalm_sha256=$PSALM_SHA"
fi
