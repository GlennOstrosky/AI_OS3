#!/bin/bash
# Look up any of the 12 Universal Laws by number.
# Usage: ./lookup_law.sh 7
N="${1:-1}"

declare -A LAW_NAME=(
  [1]="Divine Oneness"           [2]="Vibration"
  [3]="Correspondence"           [4]="Attraction"
  [5]="Inspired Action"          [6]="Perpetual Transmutation of Energy"
  [7]="Cause and Effect"         [8]="Compensation"
  [9]="Relativity"               [10]="Polarity"
  [11]="Rhythm"                  [12]="Gender"
)
declare -A LAW_LOGOS=(
  [1]="John 10:30 — I and my Father are one"
  [2]="John 6:63 — My words are spirit, and they are life"
  [3]="John 5:19 — The Son seeth the Father do"
  [4]="John 12:32 — I will draw all men unto me"
  [5]="John 9:4 — I must work the works of him that sent me"
  [6]="John 10:10 — Life more abundantly"
  [7]="John 9:39 — For judgment I am come"
  [8]="Matthew 19:29 — An hundredfold"
  [9]="Matthew 23:11 — Greatest shall be servant"
  [10]="John 8:12 — I am the light of the world"
  [11]="John 12:24 — Except a corn of wheat fall and die"
  [12]="Mark 10:8 — They twain shall be one flesh"
)

if [[ -z "${LAW_NAME[$N]}" ]]; then
  echo "Law number must be 1-12"; exit 1
fi

echo ""
echo "  Law $N: ${LAW_NAME[$N]}"
echo "  Fulfilled in the Logos: ${LAW_LOGOS[$N]}"
echo ""
