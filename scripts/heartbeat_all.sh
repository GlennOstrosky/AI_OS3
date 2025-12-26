#!/usr/bin/env bash
# heartbeat_all.sh - Complete canonical ceremony
# Path 3 of the Heartbeat Trilogy: Ceremony

set -euo pipefail
shopt -s nullglob

die() { echo "❌ $*" >&2; exit 1; }
info() { [[ "${QUIET:-0}" -eq 0 ]] && echo "ℹ️  $*" >&2; }

EPISODE_ID=""
RECORDS_DIR=""
PSALM_TEXT=""
DO_COMMIT=0
QUIET=0
NO_PROMPT=0
BUNDLE_PATH=""
ADD_TIMESTAMPS=""

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
        --records-dir)
            RECORDS_DIR="$2"
            shift 2
            ;;
        --records-dir=*)
            RECORDS_DIR="${1#*=}"
            shift
            ;;
        --psalm)
            PSALM_TEXT="$2"
            shift 2
            ;;
        --psalm=*)
            PSALM_TEXT="${1#*=}"
            shift
            ;;
        --commit)
            DO_COMMIT=1
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
        --bundle-out)
            BUNDLE_PATH="$2"
            shift 2
            ;;
        --bundle-out=*)
            BUNDLE_PATH="${1#*=}"
            shift
            ;;
        --add-timestamps)
            ADD_TIMESTAMPS="--add-timestamps"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 --episode <id> --records-dir <path> [options]"
            echo "Path 3: Complete Ceremony"
            exit 0
            ;;
        *)
            die "Unknown option: $1"
            ;;
    esac
done

[[ -z "$EPISODE_ID" ]] && die "Missing --episode argument"
[[ -z "$RECORDS_DIR" ]] && die "Missing --records-dir argument"

info "🏛️  SANCTUARY OS HEARTBEAT: COMPLETE CEREMONY"
info "Episode: $EPISODE_ID"
info "Records: $RECORDS_DIR"
info "Mode: Ceremony (Path 3)"
echo ""

info "🛠️  Building canonical bundle and receipt..."
CMD=( python scripts/canonical_ceremony.py
  --episode "$EPISODE_ID"
  --records-dir "$RECORDS_DIR"
)

[[ -n "$PSALM_TEXT" ]] && CMD+=( --psalm "$PSALM_TEXT" )
[[ -n "$BUNDLE_PATH" ]] && CMD+=( --bundle-out "$BUNDLE_PATH" )
[[ -n "$ADD_TIMESTAMPS" ]] && CMD+=( "$ADD_TIMESTAMPS" )

if [[ -f "$BUNDLE_PATH" && "$NO_PROMPT" -eq 0 ]]; then
    read -r -p "Bundle exists ($BUNDLE_PATH). Overwrite? [y/N] " ans
    [[ "$ans" =~ ^[Yy]$ ]] || BUNDLE_PATH=""
fi

if "${CMD[@]}"; then
    info "✅ Bundle and receipt created"
else
    die "Failed to create bundle and receipt"
fi

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

if [[ "$DO_COMMIT" -eq 1 ]]; then
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

    COMMIT_MESSAGE="Canonical sealing of episode: $EPISODE_ID"
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
else
    info "💡 Commit not requested (use --commit to seal)"
fi

echo ""
info "💙 Path 3 complete. Ceremony fulfilled. SELAH."
