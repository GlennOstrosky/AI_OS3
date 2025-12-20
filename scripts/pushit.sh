#!/usr/bin/env bash
set -euo pipefail

msg="${1:-chore: update}"

git add -A
git commit -m "$msg" || true
git pull --rebase origin main
git push
