#!/bin/bash
# THE PARALLEL ENGINE — Panem ↔ Reality comparison tool
# Usage: ./parallel_engine.sh
# Displays each Hunger Games parallel with its real-world counterpart

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           THE PARALLEL ENGINE — Panem ↔ Reality                    ║"
echo "║           'If we burn, you burn with us.' — Katniss                ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

declare -a PANEM=(
  "The Capitol"
  "The Districts"
  "The Hunger Games"
  "The Reaping"
  "Caesar Flickerman"
  "The Peacekeepers"
  "The Avox"
  "President Snow"
  "The Mockingjay"
  "District 12"
)

declare -a REALITY=(
  "Davos / WEF / G7 / Bilderberg"
  "Edmonton, Winnipeg, Outlook — the fading towns"
  "Manufactured crises, culture wars, fear campaigns"
  "17 Canadians/hour filing bankruptcy — reaping by paperwork"
  "Corporate media — smiling faces, approved narratives"
  "Half a billion policing, speech laws, bank freezes"
  "Citizens silenced — you know what you cannot say"
  "Politicians promising prosperity, debt at \$2.6 trillion"
  "The watchmen, the truth-tellers, the refusers"
  "Canada before the Capitol — hard work, honest people"
)

declare -a VERSE=(
  "Psalm 94:20 — Shall the throne of iniquity have fellowship with thee?"
  "Isaiah 10:1 — Woe unto them that decree unrighteous decrees"
  "Proverbs 21:6 — The getting of treasures by a lying tongue is vanity"
  "Proverbs 22:16 — He that oppresseth the poor to increase his riches shall come to want"
  "Isaiah 5:20 — Woe unto them that call evil good, and good evil"
  "Psalm 10:18 — To judge the fatherless and the oppressed"
  "Psalm 31:18 — Let the lying lips be put to silence"
  "Daniel 5:27 — Thou art weighed in the balances, and art found wanting"
  "Ezekiel 33:7 — I have set thee a watchman unto the house of Israel"
  "Psalm 137:1 — By the rivers of Babylon, there we sat down, yea, we wept"
)

for i in "${!PANEM[@]}"; do
  n=$((i + 1))
  echo "  ┌─── PARALLEL #$n ───────────────────────────────────────────"
  echo "  │ PANEM:   ${PANEM[$i]}"
  echo "  │ REALITY: ${REALITY[$i]}"
  echo "  │ VERSE:   ${VERSE[$i]}"
  echo "  └──────────────────────────────────────────────────────────────"
  echo ""
done

echo "  ════════════════════════════════════════════════════════════════"
echo "  THE HOPE: Katniss won. Not because she was the strongest."
echo "  She won because love was greater than fear."
echo "  The system was brittle underneath. It always is."
echo "  Psalm 5:10 — Let them fall by their own counsels."
echo "  The Capitol fell. And so will ours."
echo "  ════════════════════════════════════════════════════════════════"
echo ""
