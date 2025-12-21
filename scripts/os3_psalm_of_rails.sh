#!/usr/bin/env bash
set -euo pipefail

# OS3 Psalm of Rails Wrapper
# Purpose: Run the python psalm witness; if Selah (rc=0), copy proof to clipboard.
# Exit semantics:
#   0 = Selah / complete
#   9 = BLOCKED / not yet (boundary, not error)
#   1 = ERROR

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage:
  ./scripts/os3_psalm_of_rails.sh

Runs:
  python scripts/os3_psalm_of_rails.py

Behavior:
  - Always prints the proof output
  - Copies proof to clipboard only when exit code is 0 (Selah)
EOF
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v python >/dev/null 2>&1; then
  echo "ERROR: python not found in PATH" >&2
  exit 1
fi

OUT="$(mktemp)"
cleanup() { rm -f "$OUT"; }
trap cleanup EXIT

# Run once; allow rc=9 without exiting the wrapper
set +e
python scripts/os3_psalm_of_rails.py >"$OUT"
RC=$?
set -e

cat "$OUT"

if [[ "$RC" -eq 0 ]]; then
  if command -v clip.exe >/dev/null 2>&1; then
    cat "$OUT" | clip.exe
    echo "[Proof copied to clipboard]"
  else
    echo "[Clipboard not available; proof printed above]"
  fi
fi

exit "$RC"
