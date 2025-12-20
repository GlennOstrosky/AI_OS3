#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <receipt-path> <tag>" >&2
  echo "Example: $0 os3/receipts/os3_council_update_*.txt os3-council-update-v1" >&2
  exit 2
fi

RECEIPT="$1"
TAG="$2"
LEDGER="os3/ledger.jsonl"

if [[ ! -f "$RECEIPT" ]]; then
  echo "Receipt not found: $RECEIPT" >&2
  exit 3
fi

mkdir -p os3
touch "$LEDGER"

TS_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
REPO="$(pwd)"
HEAD="$(git rev-parse HEAD)"

SHA="$(python -c "import hashlib; p=r'''$RECEIPT'''; h=hashlib.sha256(); 
f=open(p,'rb')
b=f.read(1024*1024)
while b:
  h.update(b); b=f.read(1024*1024)
f.close()
print(h.hexdigest())")"

python - <<PY >> "$LEDGER"
import json
row = {
  "ts_utc": "${TS_UTC}",
  "repo": r"${REPO}",
  "head": "${HEAD}",
  "path": r"${RECEIPT}",
  "sha256": "${SHA}",
  "tag": "${TAG}"
}
print(json.dumps(row, ensure_ascii=False))
PY

echo "Appended to $LEDGER:"
tail -n 1 "$LEDGER" | python -m json.tool

echo
echo "Now verify:"
echo "  python scripts/verify_snapshot.py --last"
