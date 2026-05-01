#!/bin/bash
# Look up any of the 8 Pillars by number.
# Usage: ./lookup_pillar.sh 5
N="${1:-1}"

declare -A PILLAR=(
  [1]="TRUE — John 14:6 — I am the way, the truth, and the life"
  [2]="HONEST — 2 Cor 8:21 — Providing for honest things"
  [3]="JUST — Micah 6:8 — Do justly, love mercy, walk humbly"
  [4]="PURE — Malachi 3:3 — Refiner and purifier of silver"
  [5]="LOVELY — Song 5:16 — He is altogether lovely"
  [6]="GOOD REPORT — Proverbs 22:1 — A good name better than riches"
  [7]="VIRTUE — 2 Peter 1:5 — Add to your faith virtue (arete)"
  [8]="PRAISE — Psalm 150:6 — Let every thing that hath breath praise the LORD"
)
declare -A BEATITUDE=(
  [1]="Matthew 5:3 — Poor in spirit, theirs is the kingdom"
  [2]="Matthew 5:7 — Merciful obtain mercy"
  [3]="Matthew 5:6 — Hunger for righteousness shall be filled"
  [4]="Matthew 5:8 — Pure in heart shall see God"
  [5]="Matthew 5:5 — Meek shall inherit the earth"
  [6]="Matthew 5:9 — Peacemakers called children of God"
  [7]="Matthew 5:10 — Persecuted for righteousness, theirs is the kingdom"
  [8]="Matthew 5:12 — Rejoice and be exceeding glad"
)

if [[ -z "${PILLAR[$N]}" ]]; then
  echo "Pillar number must be 1-8"; exit 1
fi

echo ""
echo "  Pillar $N: ${PILLAR[$N]}"
echo "  Matched Beatitude: ${BEATITUDE[$N]}"
echo ""
