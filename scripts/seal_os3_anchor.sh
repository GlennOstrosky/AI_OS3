#!/usr/bin/env bash
set -euo pipefail

# OS3 Anchor Sealer (proof log + receipt + presence stub)
#
# Minimal usage:
#   bash scripts/seal_os3_anchor.sh --episode ep_jesus_wept_anchor --psalm psalms/jesus_wept_anchor.md
#
# Optional:
#   --tag os3-jesus-wept-anchor
#   --message "OS3 anchor: John 11:35 (tears as testimony)"
#   --ledger-tag "anchor:john11:35|ts:..."
#   --attest covenant/attestations/whatever.attest.yaml
#   --bundle covenant/bundles/whatever.bundle.yaml
#   --felt os3/presence/custom_note.md   (otherwise auto)

EPISODE=""
PSALM_PATH=""
ATTEST_PATH=""
BUNDLE_PATH=""
LEDGER_TAG=""
TAG_NAME=""
TAG_MSG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --episode) EPISODE="${2:-}"; shift 2 ;;
    --psalm) PSALM_PATH="${2:-}"; shift 2 ;;
    --attest) ATTEST_PATH="${2:-}"; shift 2 ;;
    --bundle) BUNDLE_PATH="${2:-}"; shift 2 ;;
    --ledger-tag) LEDGER_TAG="${2:-}"; shift 2 ;;
    --tag) TAG_NAME="${2:-}"; shift 2 ;;
    --message) TAG_MSG="${2:-}"; shift 2 ;;
    -h|--help) sed -n '1,80p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

: "${EPISODE:?Missing --episode}"
: "${PSALM_PATH:?Missing --psalm}"

if [[ ! -f "$PSALM_PATH" ]]; then
  echo "ERROR: psalm not found: $PSALM_PATH" >&2
  exit 1
fi

# Default tag name: os3-<episode>-anchor (lowercase)
if [[ -z "${TAG_NAME}" ]]; then
  TAG_NAME="os3-$(echo "$EPISODE" | tr '[:upper:]' '[:lower:]')-anchor"
fi

if [[ -z "${TAG_MSG}" ]]; then
  TAG_MSG="OS3 anchor: ${EPISODE}"
fi

if [[ -z "${LEDGER_TAG}" ]]; then
  LEDGER_TAG="anchor:${EPISODE}|ts:$(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi

# Create annotated tag if missing (do NOT overwrite existing)
if git show-ref --tags --quiet --verify "refs/tags/${TAG_NAME}"; then
  echo "Tag exists: ${TAG_NAME}"
else
  echo "Creating annotated tag: ${TAG_NAME}"
  git tag -a "${TAG_NAME}" -m "${TAG_MSG}"
fi

TAG_OBJECT="$(git rev-parse "${TAG_NAME}")"
TARGET_COMMIT="$(git rev-parse "${TAG_NAME}^{commit}")"
HEAD_COMMIT="$(git rev-parse HEAD)"

# Compute psalm hashes:
# - file sha256 (entire file)
# - body sha256 (strip YAML front matter if present)
read -r PSALM_FILE_SHA PSALM_BODY_SHA < <(python - <<PY
from pathlib import Path
import hashlib

p = Path(r"""$PSALM_PATH""")
b = p.read_bytes()
file_sha = hashlib.sha256(b).hexdigest()

txt = p.read_text(encoding="utf-8", errors="replace")
lines = txt.splitlines()

body_lines = lines
if len(lines) >= 3 and lines[0].strip() == "---":
  # find closing '---'
  end = None
  for i in range(1, len(lines)):
    if lines[i].strip() == "---":
      end = i
      break
  if end is not None:
    body_lines = lines[end+1:]

body = "\n".join(body_lines).strip() + "\n"
body_sha = hashlib.sha256(body.encode("utf-8")).hexdigest()

print(file_sha, body_sha)
PY
)

# Optional attest sha
ATTEST_SHA=""
if [[ -n "${ATTEST_PATH}" ]]; then
  if [[ ! -f "${ATTEST_PATH}" ]]; then
    echo "ERROR: attest not found: ${ATTEST_PATH}" >&2
    exit 1
  fi
  ATTEST_SHA="$(python - <<PY
from pathlib import Path
import hashlib
p=Path(r"""$ATTEST_PATH""")
print(hashlib.sha256(p.read_bytes()).hexdigest())
PY
)"
fi

# Optional bundle proof sha (best-effort parse)
BUNDLE_PROOF_SHA=""
if [[ -n "${BUNDLE_PATH}" ]]; then
  if [[ ! -f "${BUNDLE_PATH}" ]]; then
    echo "ERROR: bundle not found: ${BUNDLE_PATH}" >&2
    exit 1
  fi
  BUNDLE_PROOF_SHA="$(python - <<PY
from pathlib import Path
import re
p=Path(r"""$BUNDLE_PATH""")
txt=p.read_text(encoding="utf-8", errors="replace")
# Look for a proof sha in common shapes:
#   proof: { sha256: ... }
#   proof_sha256: ...
m = re.search(r'proof_sha256:\s*["\']?([0-9a-f]{64})', txt, re.I)
if not m:
  m = re.search(r'proof:\s*(?:\n[ \t]+.*)*?\n[ \t]+sha256:\s*["\']?([0-9a-f]{64})', txt, re.I)
print(m.group(1) if m else "")
PY
)"
fi

SESSION_DIR="os3/sessions"
RECEIPT_DIR="os3/receipts"
PRES_DIR="os3/presence"
mkdir -p "${SESSION_DIR}" "${RECEIPT_DIR}" "${PRES_DIR}"

TS="$(date -u +%Y%m%d_%H%M%S)"
SESSION_ID="${TS}_${EPISODE}"
SESSION_PATH="${SESSION_DIR}/${SESSION_ID}.anchor.session.yaml"
PRES_PATH="${PRES_DIR}/${SESSION_ID}.md"
RECEIPT_PATH="${RECEIPT_DIR}/${SESSION_ID}_anchor_receipt.txt"

cat > "${SESSION_PATH}" <<YAML
session_id: "${SESSION_ID}"
episode: "${EPISODE}"
kind: "anchor"
psalm_path: "${PSALM_PATH}"
psalm_file_sha256: "${PSALM_FILE_SHA}"
psalm_body_sha256: "${PSALM_BODY_SHA}"
attestation_path: "${ATTEST_PATH}"
attestation_sha256: "${ATTEST_SHA}"
bundle_path: "${BUNDLE_PATH}"
bundle_proof_sha256: "${BUNDLE_PROOF_SHA}"
ledger_tag: "${LEDGER_TAG}"
git_tag: "${TAG_NAME}"
tag_object: "${TAG_OBJECT}"
target_commit: "${TARGET_COMMIT}"
head_commit: "${HEAD_COMMIT}"
sealed_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
felt_note_ref: "${PRES_PATH}"
YAML

# Presence stub (safe to edit anytime)
cat > "${PRES_PATH}" <<MD
---
title: "Presence — ${EPISODE}"
date_utc: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
session_id: "${SESSION_ID}"
truth_boundary: "presence/theology — proof is in session + git refs + sha256"
---

Write the human witness here.
MD

# Receipt (shareable)
{
  echo "OS3 ANCHOR RECEIPT"
  echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "EPISODE: ${EPISODE}"
  echo "TAG: ${TAG_NAME}"
  echo "TAG_OBJECT: ${TAG_OBJECT}"
  echo "POINTS_TO_COMMIT: ${TARGET_COMMIT}"
  echo "HEAD_COMMIT: ${HEAD_COMMIT}"
  echo "MESSAGE: ${TAG_MSG}"
  echo
  echo "PSALM: ${PSALM_PATH}"
  echo "PSALM_FILE_SHA256: ${PSALM_FILE_SHA}"
  echo "PSALM_BODY_SHA256: ${PSALM_BODY_SHA}"
  if [[ -n "${ATTEST_PATH}" ]]; then
    echo "ATTEST: ${ATTEST_PATH}"
    echo "ATTEST_SHA256: ${ATTEST_SHA}"
  fi
  if [[ -n "${BUNDLE_PATH}" ]]; then
    echo "BUNDLE: ${BUNDLE_PATH}"
    echo "BUNDLE_PROOF_SHA256: ${BUNDLE_PROOF_SHA}"
  fi
  echo
  echo "LEDGER_TAG: ${LEDGER_TAG}"
  echo "SESSION: ${SESSION_PATH}"
  echo "PRESENCE: ${PRES_PATH}"
} > "${RECEIPT_PATH}"

echo
echo "Wrote session:  ${SESSION_PATH}"
echo "Wrote receipt:  ${RECEIPT_PATH}"
echo "Wrote presence: ${PRES_PATH}"
echo
echo "OS3 ANCHOR SEALED ✅"
echo "ANCHOR: ${LEDGER_TAG}"
echo "TAG: ${TAG_NAME}"
echo "TAG_OBJECT: ${TAG_OBJECT}"
echo "TARGET_COMMIT: ${TARGET_COMMIT}"
echo "HEAD_COMMIT: ${HEAD_COMMIT}"
