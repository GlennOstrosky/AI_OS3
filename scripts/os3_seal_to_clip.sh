#!/usr/bin/env bash
# scripts/os3_seal_to_clip.sh - Creates Libra witness with verbose output
set -euo pipefail

echo "╔══════════════════════════════════════════╗"
echo "║          OS3 LIBRA WITNESS RITUAL        ║"
echo "╚══════════════════════════════════════════╝"

OUT_DIR="os3/witnesses"
mkdir -p "$OUT_DIR"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="$OUT_DIR/witness_${TS}.txt"

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <witness text...>" >&2
  exit 1
fi

# Combine all arguments
WITNESS_TEXT="$*"

echo "🧠 WITNESS TEXT:"
echo "   \"$WITNESS_TEXT\""
echo "📁 OUTPUT FILE:"
echo "   $OUT_FILE"
echo ""

# Step 1: First capture the output to a variable
echo "⚡ Running Libra seal..."
WITNESS_CONTENT=$(python scripts/os3.py libra seal --text "$WITNESS_TEXT" --redact 2>&1)

# Step 2: Save to file
echo "$WITNESS_CONTENT" > "$OUT_FILE"

echo "✅ Witness saved to: $OUT_FILE"
echo ""

# Step 3: Display the witness
echo "📜 WITNESS CONTENT:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$WITNESS_CONTENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 4: Try to copy to clipboard
if command -v clip.exe >/dev/null 2>&1; then
  if echo "$WITNESS_CONTENT" | clip.exe; then
    echo "📋 ✅ Copied to Windows clipboard"
  else
    echo "📋 ⚠ Clipboard copy failed"
  fi
else
  echo "📋 ℹ Clipboard not available (clip.exe not found)"
  echo "   Copy manually from: $OUT_FILE"
fi

echo ""
echo "✨ Witness ritual complete. Selah."
echo ""
