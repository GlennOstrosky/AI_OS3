#!/usr/bin/env bash
set -euo pipefail

mkdir -p os3/receipts

TS="$(date -u +%Y-%m-%dT%H%M%SZ)"
NAME="${1:-os3_receipt}"
OUT="os3/receipts/${NAME}_${TS}.txt"

cat > "$OUT" <<EOF
OS3 RECEIPT
ts_utc: ${TS}
repo: $(pwd)
purpose: ${NAME}
note: (fill this in)
---
EOF

echo "Wrote: $OUT"
