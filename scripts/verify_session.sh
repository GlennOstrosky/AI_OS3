#!/usr/bin/env bash
set -euo pipefail

# Wrapper verifier:
# - runs python YAML session verifier
# - optionally verifies tag -> commit mapping
#
# Usage:
#   ./scripts/verify_session.sh os3/sessions/FILE.yaml [--tag SOME_TAG]

SESSION="${1:-}"
shift || true

TAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) TAG="${2:-}"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

: "${SESSION:?Missing session path}"

PYTHONUTF8=1 py scripts/os3_verify_session.py --session "$SESSION"

if [[ -n "$TAG" ]]; then
  echo
  echo "Tag mapping:"
  echo "TAG_OBJECT:   $(git rev-parse "$TAG")"
  echo "TARGET_COMMIT:$(git rev-parse "$TAG^{commit}")"
fi

echo "VERIFY COMPLETE ✅"
