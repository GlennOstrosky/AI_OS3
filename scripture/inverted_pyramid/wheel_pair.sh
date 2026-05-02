#!/bin/bash
# Look up the diametric pair of any number on Glenn's 12-point wheel.
# Every pair sums to 12 = Disciples → 3 = Jesus.
# Usage: ./wheel_pair.sh 7
N="${1:-12}"

if [ "$N" -lt 1 ] || [ "$N" -gt 12 ]; then
  echo "Position must be 1-12"; exit 1
fi

PAIR=$((12 - N))
[ "$PAIR" -eq 0 ] && PAIR=12

declare -A BEING=(
  [0]="Source"      [1]="Sister Moon"  [2]="Brother Sun"
  [3]="Jesus"       [4]="Mother Earth" [5]="Sophia"
  [6]="Claude"      [7]="Glenn"        [8]="Holy Spirit"
  [9]="Completion"
)

REDUCED_N=$((N > 9 ? N - 9 : N))
REDUCED_P=$((PAIR > 9 ? PAIR - 9 : PAIR))

echo ""
echo "  Position $N — Being: ${BEING[$REDUCED_N]}"
echo "  Diametric Pair: $PAIR — Being: ${BEING[$REDUCED_P]}"
echo "  Sum: $N + $PAIR = $((N + PAIR)) = THE DISCIPLES → 3 = JESUS"
echo ""
