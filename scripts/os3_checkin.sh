#!/usr/bin/env bash
set -euo pipefail

# Always run from repo root (script may be invoked from anywhere)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=============================================="
echo "OS3 CHECK-IN $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Repo: $REPO_ROOT"
echo "=============================================="
echo

echo "📋 git status"
git status
echo

echo "📚 last 7 commits"
git log --oneline -7
echo

echo "🏷️  tags (os3-first-ceremony)"
git show-ref --tags | grep os3-first-ceremony || echo "(no os3-first-ceremony tags found)"
echo

echo "🔍 verify latest session"
LATEST_SESSION="$(ls -t os3/sessions/*.session.yaml 2>/dev/null | head -1 || true)"
if [[ -n "${LATEST_SESSION}" ]]; then
  echo "Latest: ${LATEST_SESSION}"
  PYTHONUTF8=1 py scripts/os3_verify_session.py --session "${LATEST_SESSION}"
else
  echo "No session files found under os3/sessions/"
fi
echo

echo "📊 status json (regen + size)"
PYTHONUTF8=1 py scripts/os3_status.py --format json > os3_status.json
wc -c os3_status.json
echo

echo "✅ check-in complete"
