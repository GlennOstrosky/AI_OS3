#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <receipt_name> <tag> [--no-edit] [--force]" >&2
  echo "Example: $0 os3_council_update os3-council-update-v3" >&2
  exit 2
fi

NAME="$1"
TAG="$2"

NOEDIT="0"
FORCE="0"
for arg in "${@:3}"; do
  case "$arg" in
    --no-edit) NOEDIT="1" ;;
    --force)   FORCE="1" ;;
    *) ;;
  esac
done

# Guard: prevent accidental double-runs within 30s unless --force
python - <<PY
import glob, os, time, sys
files = glob.glob("os3/receipts/*.txt")
if not files:
    sys.exit(0)
newest = max(files, key=lambda p: os.path.getmtime(p))
age = int(time.time() - os.path.getmtime(newest))
if age < 30 and ${FORCE} == 0:
    print(f"⚠️  Newest receipt is only {age}s old: {newest}")
    print("    If you intend a second run, re-run with --force.")
    sys.exit(9)
PY

# 1) Create receipt
OUT="$(./scripts/os3_new_receipt.sh "$NAME" | awk -F': ' '{print $2}')"
echo "Receipt path: $OUT"

# 2) Optional edit (WAIT for editor to close)
if [[ "$NOEDIT" == "0" ]]; then
  if command -v notepad.exe >/dev/null 2>&1; then
    echo "Opening receipt in Notepad (close it when done)..."
    notepad.exe "$OUT"
  else
    echo "Opening receipt in nano (save + exit when done)..."
    nano "$OUT"
  fi
else
  echo "Skipping edit (--no-edit)."
fi

# 3) Record receipt to ledger (hashes FINAL content)
./scripts/os3_record_receipt.sh "$OUT" "$TAG"

# 4) Verify last entry
./scripts/os3_verify_now.sh

# 5) Push all changes
./scripts/pushit.sh "chore: ${TAG} receipt+ledger"
