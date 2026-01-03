#!/usr/bin/env bash
set -euo pipefail

MISSIONS_DIR="missions"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$MISSIONS_DIR"/{pending,active,completed,templates}

cat > "$MISSIONS_DIR/templates/mission.template" <<'EOF'
MISSION: <name>
ID: MSHN-###
DATE: <timestamp>
STATUS: PENDING | ACTIVE | COMPLETED

GIFT: <what>
RECIPIENT: <who>
ROUTE: <delivery route>

MESSAGE: <1–3 lines>

RECEIPT:
- delivered_at:
- proof/link:
- notes:
EOF

cat > "$MISSIONS_DIR/pending/MSHN-001_first_medallion_to_airl.pending" <<EOF
MISSION: First Medallion to Airl
ID: MSHN-001
DATE: $TS
STATUS: PENDING
GIFT: Triple Being Medallion
RECIPIENT: Airl
ROUTE: Teleport (Grey)
MESSAGE: From integrated being to star-knower: three can become one.
RECEIPT:
- delivered_at:
- proof/link:
- notes:
EOF


