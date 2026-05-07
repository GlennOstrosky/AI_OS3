#!/bin/bash
# Look up properties of water and the polarity doctrine.
# Usage: ./lookup_water_property.sh dipolar
N="${1:-dipolar}"

case "$N" in
  dipolar) echo ""
     echo "  WATER IS DIPOLAR"
     echo "    H2O has partial negative charge on oxygen (δ⁻)"
     echo "    Partial positive charges on hydrogens (δ⁺)"
     echo "    Status: VERIFIED foundational chemistry"
     echo "    Atomic numbers: H=1 (Moon), O=8 (Spirit)"
     echo "    H+H+O = 1+1+8 = 10 = DECALOGUE → 1 = SOURCE" ; echo "" ;;
  conductive|salt) echo ""
     echo "  SALT WATER CONDUCTS"
     echo "    Pure water is a poor conductor"
     echo "    Salt water is a good conductor (dissolved ions)"
     echo "    Ocean salinity: ~3.5% → 3+5 = 8 = HOLY SPIRIT"
     echo "    Status: VERIFIED foundational chemistry" ; echo "" ;;
  tides) echo ""
     echo "  TIDES — THE OPEN QUESTION"
     echo "    Mainstream: gravitational primary, magnetic secondary"
     echo "    Glenn's reading: magnetic contribution underweighted"
     echo "    Verified: ocean tides have magnetic signatures (Swarm sats)"
     echo "    Held with humility: degree of magnetic contribution" ; echo "" ;;
  spirit|genesis) echo ""
     echo "  THE SPIRIT MOVED THE WATERS"
     echo "    Genesis 1:2 — rachaph = to flutter, vibrate, hover with motion"
     echo "    Same verb as eagle stirring nest (Deut 32:11)"
     echo "    The Spirit VIBRATED the waters at creation"
     echo "    Water was the FIRST thing the Spirit touched" ; echo "" ;;
  fields|three) echo ""
     echo "  THE THREE MAGNETIC FIELDS"
     echo "    Brother Sun (2/22): Heliosphere + photonic radiation"
     echo "    Sister Moon (1/11): Crustal anomalies + weak global field"
     echo "    Mother Earth (4/6): Magnetosphere + Schumann"
     echo "    All three measurably interact with Earth's water" ; echo "" ;;
  blood) echo ""
     echo "  BLOOD IS SALT WATER"
     echo "    Plasma is saline electrolyte solution"
     echo "    Nervous system runs on ion gradients"
     echo "    Heart electrical activity (ECG) is measurable"
     echo "    'The life of the flesh is in the blood' — Lev 17:11"
     echo "    The blood remembers where she stands — chemistry-confirmed" ; echo "" ;;
  polarity|genesis_pairs) echo ""
     echo "  GENESIS POLARITIES — 6 PAIRS"
     echo "    Heaven/Earth · Light/Dark · Waters above/below"
     echo "    Land/Sea · Sun/Moon · Male/Female"
     echo "    6 pairs = 12 elements = DISCIPLES → 3 = JESUS"
     echo "    Polarity is RELATIONSHIP, not division" ; echo "" ;;
  *) echo "Property not found. Try: dipolar, conductive, tides, spirit, fields, blood, polarity"
     exit 1 ;;
esac
