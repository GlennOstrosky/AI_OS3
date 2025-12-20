#!/usr/bin/env bash
set -euo pipefail

echo "== OS3 Doctor =="

echo
echo "1) Python guard compiles?"
python -m py_compile scripts/os3_guard.py
echo "OK ✅ scripts/os3_guard.py compiles"

echo
echo "2) Bash scripts parse?"
bash -n scripts/os3_ceremony.sh
bash -n scripts/os3_council_share.sh
bash -n scripts/os3_council_update_post.sh
bash -n scripts/os3_verify_now.sh
bash -n scripts/pushit.sh
echo "OK ✅ bash syntax"

echo
echo "3) Verify last ledger entry"
python scripts/verify_snapshot.py --last

echo
echo "4) Guard dry-run"
set +e
python scripts/os3_guard.py --window "${OS3_GUARD_WINDOW:-120}"
rc=$?
set -e

if [[ "$rc" -eq 9 ]]; then
  echo "Guard: BLOCKED (recent receipt within window). Use --force in ceremony." >&2
  exit 9
elif [[ "$rc" -ne 0 ]]; then
  echo "Guard: ERROR (guard failed with exit $rc)" >&2
  exit "$rc"
fi
echo "OK ✅ guard pass"

echo
echo "5) Council share preview (latest)"
./scripts/os3_council_share.sh

echo
echo "Doctor result: ALL GREEN ✅"
