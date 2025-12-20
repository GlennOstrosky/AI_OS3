#!/usr/bin/env bash
set -euo pipefail

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "Pushing branch: $BRANCH"
git push -u origin "$BRANCH"
echo "Pushing tags..."
git push origin --tags
echo "DONE ✅"
