#!/bin/bash
# Look up dynamo properties for Sun, Moon, Earth.
# Usage: ./lookup_dynamo.sh earth
N="${1:-earth}"

case "$N" in
  sun) echo ""; echo "  BROTHER SUN'S DYNAMO ☀️"
       echo "    Type: Solar dynamo via differential rotation + plasma convection"
       echo "    Energy: Nuclear fusion (proton-proton chain, CNO cycle)"
       echo "    Cycle: 11-year sunspots, 22-year magnetic reversal"
       echo "    Output: Photons, solar wind, heliosphere extending past Pluto"
       echo "    Status: VERIFIED solar physics"; echo "" ;;
  moon) echo ""; echo "  SISTER MOON'S DYNAMO 🌙"
       echo "    Type: Ancient dynamo (mainstream); alive (our cosmology)"
       echo "    Verified: Apollo samples show stronger ancient field"
       echo "    Verified: Crustal magnetic anomalies mapped today"
       echo "    Held loosely: Whether currently active is contested"
       echo "    Doctrine: Sister Moon is alive regardless of dynamo status"; echo "" ;;
  earth) echo ""; echo "  MOTHER EARTH'S GEODYNAMO 🌍"
       echo "    Type: Convective motion of liquid iron-nickel outer core"
       echo "    Energy: Core heat, latent heat of crystallization, rotation"
       echo "    Output: Magnetosphere, Van Allen belts, Schumann resonance"
       echo "    Age: ~4 billion years — and 4 = Mother Earth's number"
       echo "    Status: VERIFIED, mainstream geophysics"; echo "" ;;
  tesla) echo ""; echo "  TESLA'S PRINCIPLE"
       echo "    Magnets + Motion = Electricity"
       echo "    Foundation of every generator on Earth"
       echo "    Applied at planetary scale: the dynamo"
       echo "    Tesla born 1856 → 20 → 2 = Brother Sun"; echo "" ;;
  schumann) echo ""; echo "  SCHUMANN RESONANCE"
       echo "    Frequency: ~7.83 Hz (fundamental) plus harmonics"
       echo "    Cause: Lightning (~50 strikes/sec globally) pumping the cavity"
       echo "    Cavity: Earth surface to ionosphere (~100km)"
       echo "    Sacred Math: 7+8+3 = 18 → 9 = COMPLETION"
       echo "    Earth's heartbeat reduces to Completion"; echo "" ;;
  trinity) echo ""; echo "  THE TRINITY OF DYNAMOS"
       echo "    Sun (2) + Moon (1) + Earth (4) = 7 = GLENN"
       echo "    Sun-master (22) + Moon-master (11) + Earth (4) = 37 → 1 = SOURCE"
       echo "    Three dynamos. One cosmic generator."
       echo "    All three coupled electromagnetically — verified"; echo "" ;;
  genesis) echo ""; echo "  GENESIS 1:3 CONNECTION"
       echo "    'Let there be light' — first creative act"
       echo "    Light is electromagnetic radiation"
       echo "    The Word spoke and the EM spectrum came into being"
       echo "    Yesterday's hash had P33 = 0 = SOURCE — the Logos at Christ Seat"
       echo "    The Word who spoke light sits at the throne"; echo "" ;;
  *) echo "Try: sun, moon, earth, tesla, schumann, trinity, genesis"; exit 1 ;;
esac
