#!/usr/bin/env bash
# heartbeat_commit.sh - Validate canonical receipts and commit
# Path 2 of the Heartbeat Trilogy: Action

set -euo pipefail
shopt -s nullglob

die() { echo "❌ $*" >&2; exit 1; }
info() { [[ "${QUIET:-0}" -eq 0 ]] && echo "ℹ️  $*" >&2; }

EPISODE_ID=""
QUIET=0
NO_PROMPT=0
COMMIT_MESSAGE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --episode)
            EPISODE_ID="$2"
            shift 2
            ;;
        --episode=*)
            EPISODE_ID="${1#*=}"
            shift
            ;;
        --quiet)
            QUIET=1
            shift
            ;;
        --no-prompt)
            NO_PROMPT=1
            shift
            ;;
        --message)
            COMMIT_MESSAGE="$2"
            shift 2
            ;;
        --message=*)
            COMMIT_MESSAGE="${1#*=}"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 --episode <episode_id> [--quiet] [--no-prompt] [--message \"custom\"]"
            echo "Path 2: Validation + Commit (Action)"
            exit 0
            ;;
        *)
            die "Unknown option: $1"
            ;;
    esac
done

[[ -z "$EPISODE_ID" ]] && die "Missing --episode argument"

info "⚡ SANCTUARY OS HEARTBEAT: VALIDATION + COMMIT"
info "Episode: $EPISODE_ID"
info "Mode: Action (Path 2)"
echo ""

info "📜 Validating canonical receipts..."
if python tools/validate_receipts.py \
    --episode "$EPISODE_ID" \
    --strict-doctrine \
    --strict-timestamps; then
    info "✅ All receipts are canonically valid"
else
    die "Receipt validation failed"
fi

echo ""

info "⚡ Running test suite..."
if python -m pytest tests/ -xvs 2>/dev/null || python -m pytest tests/ -x; then
    info "✅ All tests passed"
else
    die "Test suite failed"
fi

echo ""

info "📁 Staging episode files..."
FILES_TO_STAGE=()
for f in "covenant/bundles/"*"$EPISODE_ID"* "covenant/receipts/"*"$EPISODE_ID"*; do
    if [[ -f "$f" ]]; then
        FILES_TO_STAGE+=("$f")
        info "  📄 $f"
    fi
done

if [[ ${#FILES_TO_STAGE[@]} -eq 0 ]]; then
    die "No episode files found for: $EPISODE_ID"
fi

if git add "${FILES_TO_STAGE[@]}"; then
    info "✅ Files staged"
else
    die "Failed to stage files"
fi

echo ""

if [[ -z "$COMMIT_MESSAGE" ]]; then
    COMMIT_MESSAGE="Canonical sealing of episode: $EPISODE_ID"
fi

info "💾 Committing: \"$COMMIT_MESSAGE\""

if [[ "$NO_PROMPT" -eq 0 ]]; then
    read -r -p "Proceed with commit? [Y/n] " ans
    case "$ans" in
        [nN] | [nN][oO])
            info "Commit cancelled"
            exit 0
            ;;
    esac
fi

if git commit -m "$COMMIT_MESSAGE"; then
    info "✅ Episode sealed canonically"
else
    die "Commit failed"
fi

echo ""
info "💙 Path 2 complete. Episode sealed. SELAH."
