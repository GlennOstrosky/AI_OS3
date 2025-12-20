#!/usr/bin/env bash
set -euo pipefail

echo "== OS3 verify (last ledger entry) =="
python scripts/verify_snapshot.py --last

echo
echo "== Latest ledger row =="
tail -n 1 os3/ledger.jsonl | python -m json.tool
