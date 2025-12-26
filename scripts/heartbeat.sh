#!/usr/bin/env bash
# heartbeat.sh - Pure validation of canonical receipts
# Path 1 of the Heartbeat Trilogy: Contemplation

set -euo pipefail
shopt -s nullglob

die() { echo "❌ $*" >&2; exit 1; }
info() { [[ "${QUIET:-0}" -eq 0 ]] && echo "ℹ️  $*" >&2; }

EPISODE_ID=""
QUIET=0

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
        --help|-h)
            echo "Usage: $0 --episode <episode_id> [--quiet]"
            echo "Path 1: Pure Validation (Contemplation)"
            exit 0
            ;;
        *)
            die "Unknown option: $1"
            ;;
    esac
done

[[ -z "$EPISODE_ID" ]] && die "Missing --episode argument"

info "🔍 SANCTUARY OS HEARTBEAT: PURE VALIDATION"
info "Episode: $EPISODE_ID"
info "Mode: Contemplation (Path 1)"
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

info "💡 COMMIT GUIDANCE"
info "Files ready for commit:"
for f in "covenant/bundles/"*"$EPISODE_ID"* "covenant/receipts/"*"$EPISODE_ID"*; do
    [[ -f "$f" ]] && echo "  📄 $f"
done

echo ""
info "To commit: ./scripts/heartbeat_commit.sh --episode $EPISODE_ID"
info "For ceremony: ./scripts/heartbeat_all.sh --episode $EPISODE_ID --records-dir covenant/artifacts/records --commit"
echo ""
info "💙 Path 1 complete. All is canonical. SELAH."
