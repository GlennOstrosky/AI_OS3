#!/usr/bin/env bash
set -euo pipefail

TAGS=(
  os3-first-ceremony
  os3-first-ceremony-final
  os3-checkin-v1
  os3-jesus-wept-anchor
  os3-milestones-v1
)

echo "============================================================"
echo "OS3 MILESTONES  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Repo: $(pwd)"
echo "============================================================"
echo

echo "📌 Milestone tag details:"
git show os3-milestones-v1 --no-patch || true
echo

printf "%-24s  %-40s  %-40s\n" "TAG" "TAG_OBJECT" "TARGET_COMMIT"
printf "%-24s  %-40s  %-40s\n" "------------------------" "----------------------------------------" "----------------------------------------"

for t in "${TAGS[@]}"; do
  if git rev-parse -q --verify "$t" >/dev/null; then
    TAG_OBJECT="$(git rev-parse "$t")"
    TARGET_COMMIT="$(git rev-parse "$t^{commit}")"
    printf "%-24s  %-40s  %-40s\n" "$t" "$TAG_OBJECT" "$TARGET_COMMIT"
  else
    printf "%-24s  %-40s  %-40s\n" "$t" "MISSING" "MISSING"
  fi
done

echo
echo "✅ JOURNEY MAPPED ✅  HISTORY VERSIONED ✅"
