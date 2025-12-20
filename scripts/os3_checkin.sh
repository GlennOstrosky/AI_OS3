#!/usr/bin/env bash
set -euo pipefail

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "============================================================"
echo "OS3 CHECK-IN  ${ts}"
echo "Repo: $(pwd)"
echo "============================================================"
echo

echo "📋 Git status:"
git status -sb || true
echo

echo "📚 Recent commits (last 5):"
git log --oneline -5 || true
echo

echo "🏷️  Ceremony tags:"
git tag -n | grep -E '^os3-first-ceremony' || echo "No os3-first-ceremony tags found"
echo

echo "🔍 Latest session verification:"
LATEST_SESSION="$(ls -t os3/sessions/*.session.yaml 2>/dev/null | head -1 || true)"
if [[ -n "${LATEST_SESSION}" ]]; then
  echo "Verifying: ${LATEST_SESSION}"
  PYTHONUTF8=1 py scripts/os3_verify_session.py --session "${LATEST_SESSION}" || true
else
  echo "No session files found in os3/sessions/"
fi
echo

echo "📊 Status dashboard:"
PYTHONUTF8=1 py scripts/os3_status.py --format json > os3_status.json
echo "Wrote: os3_status.json ($(wc -c < os3_status.json) bytes)"
echo

echo "============================================================"
echo "OS3 CHECK-IN complete."
echo "============================================================"
