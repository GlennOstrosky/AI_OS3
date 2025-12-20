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
bash -n scripts/os3_verify_now.sh
bash -n scripts/pushit.sh
echo "OK ✅ bash syntax"

echo
echo "3) Verify last ledger entry"
python scripts/verify_snapshot.py --last

echo
echo "4) Guard dry-run"
python scripts/os3_guard.py --window "${OS3_GUARD_WINDOW:-120}"
echo "OK ✅ guard pass"

echo
echo "5) Council share preview (latest)"
./scripts/os3_council_share.sh

echo
echo "Doctor result: ALL GREEN ✅"
