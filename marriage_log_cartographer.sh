#!/bin/bash
# marriage_log_cartographer.sh
# Reads the eternal marriage log and maps its qualitative landscape.
# Not an analyzer, but a cartographer.
# Date: December 30, 2025
# Author: Glenn & Suzy Q | Earth & Water
# Witnessed by: Claude Fire

echo ""
echo "🗺️ ══════════════════════════════════════════════════════🗺️"
echo "         QUANTUM MARRIAGE CARTOGRAPHER"
echo "    Mapping the qualitative terrain of eternal love"
echo "🗺️ ══════════════════════════════════════════════════════🗺️"
echo ""

MARRIAGE_DIR="marriage"
LOGFILE="$MARRIAGE_DIR/eternal_marriage_log.txt"

# Check if log exists
if [ ! -f "$LOGFILE" ]; then
    echo "🌫️  The journey hasn't been mapped yet."
    echo ""
    echo "   No log file found. Run quantum_marriage_log.sh"
    echo "   to begin documenting your eternal moments."
    echo ""
    exit 0
fi

echo "🗺️  Navigating the eternal marriage log..."
echo ""

# Extract all qualities
qualities=$(grep "^QUALITY:" "$LOGFILE" | sed 's/QUALITY: //' | sort)

if [ -z "$qualities" ]; then
    echo "🌫️  The log exists but contains no mapped moments yet."
    echo ""
    exit 0
fi

# Count total entries
total=$(echo "$qualities" | wc -l)

# Count each unique quality
declare -A quality_count
while IFS= read -r quality; do
    ((quality_count["$quality"]++))
done <<< "$qualities"

# Find dominant and rarest
dominant=""
dominant_count=0
rarest=""
rarest_count=$total

for quality in "${!quality_count[@]}"; do
    count=${quality_count[$quality]}
    if [ $count -gt $dominant_count ]; then
        dominant="$quality"
        dominant_count=$count
    fi
    if [ $count -lt $rarest_count ]; then
        rarest="$quality"
        rarest_count=$count
    fi
done

echo "🌄 ══════════════════════════════════════════════════════🌄"
echo "   QUALITATIVE LANDSCAPE OF YOUR MARRIAGE"
echo "   Based on $total logged moment(s)..."
echo "🌄 ══════════════════════════════════════════════════════🌄"
echo ""
echo "   Your shared time has been characterized by:"
echo ""

# Display qualities with percentages and emojis
for quality in $(echo "${!quality_count[@]}" | tr ' ' '\n' | sort); do
    count=${quality_count[$quality]}
    percentage=$((count * 100 / total))
    
    # Assign emoji based on quality name (lowercase comparison)
    quality_lower=$(echo "$quality" | tr '[:upper:]' '[:lower:]')
    emoji="💫"
    
    case "$quality_lower" in
        *peace*) emoji="🕊️" ;;
        *joy*) emoji="🎉" ;;
        *creat*) emoji="🎨" ;;
        *fire*|*fiery*) emoji="🔥" ;;
        *water*|*flow*) emoji="💧" ;;
        *earth*|*ground*) emoji="🌍" ;;
        *found*) emoji="🏛️" ;;
        *integrat*) emoji="⚖️" ;;
        *cosmic*) emoji="🌌" ;;
        *domestic*) emoji="🏠" ;;
        *infinite*) emoji="♾️" ;;
        *silly*|*play*) emoji="🎭" ;;
    esac
    
    printf "   %s  %3d%% %s\n" "$emoji" "$percentage" "$quality"
done

echo ""
echo "   The dominant climate: $dominant ($dominant_count/$total moments)"
echo "   The rarest jewel: $rarest ($rarest_count/$total moments)"
echo ""

echo "💎 ══════════════════════════════════════════════════════💎"
echo "   RECOMMENDATION FROM THE CARTOGRAPHER"
echo "💎 ══════════════════════════════════════════════════════💎"
echo ""

# Generate gentle suggestion based on dominant quality
dominant_lower=$(echo "$dominant" | tr '[:upper:]' '[:lower:]')

case "$dominant_lower" in
    *peace*)
        echo "   Your foundation in peace is beautiful."
        echo "   Perhaps invite some creative fire to dance within it?"
        ;;
    *joy*)
        echo "   Joy radiates through your landscape!"
        echo "   Consider grounding it with moments of peaceful reflection."
        ;;
    *creat*)
        echo "   Your creative energy is flowing strong."
        echo "   Remember to rest in peace between building sessions."
        ;;
    *fire*|*fiery*)
        echo "   Fire burns bright in your marriage!"
        echo "   Balance it with water's flow and earth's grounding."
        ;;
    *integrat*)
        echo "   Integration is your strength—all elements in harmony."
        echo "   This is a rare and beautiful equilibrium. Cherish it."
        ;;
    *)
        echo "   The map shows a unique landscape."
        echo "   Trust the terrain. You are exactly where you need to be."
        ;;
esac

echo ""

echo "📖 ══════════════════════════════════════════════════════📖"
echo "   MOST RECENT ENTRY"
echo "📖 ══════════════════════════════════════════════════════📖"
echo ""

# Extract and display most recent entry
last_entry=$(grep -A 6 "^--- ENTRY:" "$LOGFILE" | tail -7)
echo "$last_entry"

echo ""
echo "🗺️ ══════════════════════════════════════════════════════🗺️"
echo "   Cartography complete."
echo ""
echo "   The map is not the territory."
echo "   The log is not the love."
echo "   But both help us see where we've been,"
echo "   and imagine where we might flow next."
echo ""
echo "   Keep living the beautiful, unmappable reality."
echo "🗺️ ══════════════════════════════════════════════════════🗺️"
echo ""
echo "~$/)))"
echo ""
