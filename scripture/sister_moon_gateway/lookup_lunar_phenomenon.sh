#!/bin/bash
# Look up Sister Moon's verified influences on Earth.
# Usage: ./lookup_lunar_phenomenon.sh tides
N="${1:-tides}"

case "$N" in
  tides) echo ""
     echo "  TIDES"
     echo "    Mainstream: Gravitational pull (real, verified)"
     echo "    Honest: Tidal complexity not perfectly explained by simple gravity"
     echo "    Loving: Conductive salt water in coupled magnetic fields"
     echo "    Both/and — gravity AND magnetism participate" ; echo "" ;;
  blood|menstrual) echo ""
     echo "  BLOOD AND MENSTRUAL CYCLE"
     echo "    Cycle: ~28 days (human) vs ~29.5 days (lunar)"
     echo "    Verified: Pineal gland contains magnetite, endocrine is electromagnetic"
     echo "    Verified: Blood is salt water, responds to magnetic fields"
     echo "    Teaching: The Moon rules the blood — the blood remembers where she stands"
     echo "    Scripture: Lev 17:11 — The life of the flesh is in the blood" ; echo "" ;;
  weather) echo ""
     echo "  WEATHER"
     echo "    Verified: Lunar phase correlates with geomagnetic activity"
     echo "    Verified: Lunar tidal effect on atmosphere is measurable"
     echo "    Reading: Moon's magnetism shapes jet streams, storm tracks" ; echo "" ;;
  earthquakes|seismic) echo ""
     echo "  EARTHQUAKES AND VOLCANISM"
     echo "    Verified: Earthquake clustering around full and new moons"
     echo "    Verified: Lunar perigee correlates with seismic activity"
     echo "    Reading: Moon's field exerts electromagnetic stress on the crust" ; echo "" ;;
  emotion|emotions|lunatic) echo ""
     echo "  HUMAN EMOTIONS"
     echo "    Verified: ER staffing increases at full moons (persistent pattern)"
     echo "    Etymology: 'Lunatic' from Latin luna (moon)"
     echo "    Reading: We are electrochemical beings — brain electric, blood ion"
     echo "    Sister Moon's magnetic flux modulates our bioelectric fields" ; echo "" ;;
  fields|magnetic) echo ""
     echo "  THREE MAGNETIC FIELDS"
     echo "    Brother Sun (2/22): Heliosphere — solar wind — coronal events"
     echo "    Sister Moon (1/11): Crustal anomalies + weak global field"
     echo "    Mother Earth (4/6): Magnetosphere — Van Allen belts — Schumann"
     echo "    Sum: 2+1+4 = 7 = Glenn the Bridge"
     echo "    Masters: 22+11 = 33 = Christ's Master" ; echo "" ;;
  *) echo "Phenomenon not found. Try: tides, blood, weather, earthquakes, emotion, fields"
     exit 1 ;;
esac
