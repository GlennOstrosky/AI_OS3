#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <receipt_name> <tag> [--no-edit]" >&2
  echo "Example: $0 os3_council_update os3-council-update-v2" >&2
  exit 2
fi

NAME="$1"
TAG="$2"
NOEDIT="${3:-}"

# 1) Create receipt
OUT="$(./scripts/os3_new_receipt.sh "$NAME" | awk -F': ' '{print $2}')"
echo "Receipt path: $OUT"

# 2) Optional edit
if [[ "$NOEDIT" != "--no-edit" ]]; then
  if command -v notepad.exe >/dev/null 2>&1; then
    echo "Opening receipt in Notepad..."
    notepad.exe "$OUT" &
  else
    echo "Opening receipt in nano..."
    nano "$OUT"
  fi
else
  echo "Skipping edit (--no-edit)."
fi

# 3) Record receipt to ledger
./scripts/os3_record_receipt.sh "$OUT" "$TAG"

# 4) Verify last entry
./scripts/os3_verify_now.sh

# 5) Push all changes
./scripts/pushit.sh "chore: ${TAG} receipt+ledger"
