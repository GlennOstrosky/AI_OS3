#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 <snapshot-path> | --last
  <snapshot-path>   Path to receipt/snapshot file to verify
  --last            Verify the last ledger entry and its referenced file
EOF
  exit 2
}

if [[ $# -lt 1 ]]; then
  usage
fi

LEDGER="os3/ledger.jsonl"
if [[ ! -f "$LEDGER" ]]; then
  echo "Ledger not found: $LEDGER" >&2
  exit 3
fi

if [[ "$1" == "--last" ]]; then
  ENTRY_LINE="$(tail -n 1 "$LEDGER" || true)"
  if [[ -z "$ENTRY_LINE" ]]; then
    echo "No ledger entries found in $LEDGER" >&2
    exit 4
  fi
  echo "=== Last ledger entry ==="
  echo "$ENTRY_LINE" | python -m json.tool

  SNAP_PATH="$(echo "$ENTRY_LINE" | python -c 'import sys,json; print(json.load(sys.stdin)["path"])')"
  LEDGER_SHA="$(echo "$ENTRY_LINE" | python -c 'import sys,json; print(json.load(sys.stdin).get("sha256",""))')"
else
  SNAP_PATH="$1"
  LEDGER_SHA=""
fi

if [[ ! -f "$SNAP_PATH" ]]; then
  echo "Snapshot/receipt file not found: $SNAP_PATH" >&2
  exit 5
fi

echo
echo "=== File info ==="
ls -la "$SNAP_PATH"

echo
echo "=== Compute SHA256 ==="
SNAP_HASH="$(sha256sum "$SNAP_PATH" | awk '{print $1}')"
echo "file_sha256: $SNAP_HASH"

# If we know ledger_sha from --last, compare directly
if [[ -n "$LEDGER_SHA" ]]; then
  echo "ledger sha256: $LEDGER_SHA"
  if [[ "$LEDGER_SHA" == "$SNAP_HASH" ]]; then
    echo "MATCH ✅ (file hash equals ledger sha256)"
  else
    echo "MISMATCH ❌ (file hash differs from ledger sha256)"
    exit 10
  fi
else
  # Otherwise, find any ledger line referencing this path
  MATCHING="$(grep -nF "\"path\": \"$SNAP_PATH\"" "$LEDGER" || true)"
  if [[ -z "$MATCHING" ]]; then
    echo
    echo "No ledger entry references this snapshot path."
    exit 0
  fi

  echo
  echo "=== Ledger entries referencing this snapshot ==="
  echo "$MATCHING" | while IFS= read -r line; do
    lineno="$(echo "$line" | cut -d: -f1)"
    entry="$(sed -n "${lineno}p" "$LEDGER")"
    echo "$entry" | python -m json.tool
    ledger_hash="$(echo "$entry" | python -c 'import sys,json; print(json.load(sys.stdin).get("sha256",""))')"
    echo "ledger sha256: $ledger_hash"
    if [[ "$ledger_hash" == "$SNAP_HASH" ]]; then
      echo "MATCH ✅"
    else
      echo "MISMATCH ❌"
      exit 11
    fi
    echo "----"
  done
fi

exit 0
