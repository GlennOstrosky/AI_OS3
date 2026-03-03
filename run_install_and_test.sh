#!/usr/bin/env bash
set -euo pipefail

# Detect Python launcher
if command -v py >/dev/null 2>&1; then
  PY="py -3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "ERROR: No Python found. Install Python or enable App Execution Alias, then re-run." >&2
  exit 2
fi

echo "Using Python: $($PY --version 2>&1 | head -n1)"

# Write candidate rule file
cat > candidate_rules_gravity.py <<'PYEOF'
# candidate_rules_gravity.py
"""
Candidate rule: double-slit with gravity bias.
Install via: python3 rules_manager.py candidate_rules_gravity.py --author "Glenn"
"""

import math
import random

WIDTH = 41
HEIGHT = 21
SOURCE_X = 2
SLIT_X = 10
SLIT_Y = [9, 11]
DETECTOR_X = 30

GRAVITY_STRENGTH = 0.25

def path_probability(x, y):
    dx = x - SOURCE_X
    dy = y - HEIGHT // 2
    r = math.hypot(dx, dy) + 1e-6
    base = 1.0 / (1 + 0.05 * r * r)
    gravity_factor = (y / max(1, HEIGHT - 1))
    gravity_bias = 1.0 + GRAVITY_STRENGTH * gravity_factor
    return max(0.0, min(1.0, base * gravity_bias))

def compute_pixel(x, y, world, context):
    if context.get("observer"):
        p = path_probability(x, y)
        return 1 if random.random() < p else 0

    amp = 0+0j
    for slit_y in SLIT_Y:
        dx = x - SLIT_X
        dy = y - slit_y
        r = math.hypot(dx, dy) + 1e-6
        phase = (r % 10) / 10 * 2 * math.pi
        amp += (1.0 / (1 + 0.02 * r)) * complex(math.cos(phase), math.sin(phase))

    intensity = (amp.real**2 + amp.imag**2)
    prob = 1 - math.exp(-intensity * 0.5)
    gravity_factor = (y / max(1, HEIGHT - 1))
    prob = prob * (1.0 + GRAVITY_STRENGTH * 0.5 * gravity_factor)
    return 1 if random.random() < prob else 0

def on_step(world, step):
    if step % 200 == 0:
        global SLIT_Y
        new = []
        for sy in SLIT_Y:
            delta = random.choice([-1, 0, 1])
            ny = max(1, min(HEIGHT - 2, sy + delta))
            new.append(ny)
        SLIT_Y = new
PYEOF

# Write test file (overwrite if exists)
mkdir -p tests
cat > tests/test_gravity.py <<'PYEOF'
from pathlib import Path
from quantum_world import World, RuleEngine

def test_gravity_bias(tmp_path):
    p = tmp_path / "candidate_rules_gravity.py"
    p.write_text(Path("candidate_rules_gravity.py").read_text())
    rules = RuleEngine(str(p))
    w = World(41, 21, rules)
    top_hits = sum(w.observe(30, y, {"observer": True}) for y in range(0, 7))
    w.reset()
    bottom_hits = sum(w.observe(30, y, {"observer": True}) for y in range(14, 21))
    assert bottom_hits >= top_hits
PYEOF

echo "Files written: candidate_rules_gravity.py, tests/test_gravity.py"

# Validate and install rule (creates rules_versions/ and rules_manifest.json)
echo "Validating and installing rule..."
$PY rules_manager.py candidate_rules_gravity.py --author "Glenn"

# Ensure pytest is installed
echo "Ensuring pytest is installed..."
$PY -m pip install --upgrade pip pytest >/dev/null

# Run tests
echo "Running pytest..."
$PY -m pytest -q

# Stage files for commit
echo "Staging files..."
git add candidate_rules_gravity.py tests/test_gravity.py rules_versions rules_manifest.json rules_double_slit.py || true

# Commit
MSG="Install gravity-biased double-slit rule (candidate_rules_gravity) — validated and versioned

- Added candidate_rules_gravity.py (gravity-biased double-slit plugin)
- Validated and installed via rules_manager.py (versioned under rules_versions/)
- Added tests/test_gravity.py to assert downward bias behavior
- Updated rules_manifest.json and rules_double_slit.py (active plugin)
"
git commit -m "$MSG" || { echo "Nothing to commit or commit failed."; }

# Push branch (current branch)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push -u origin "$BRANCH" || echo "Push failed; check remote or network."

# Print new commit hash
echo "Latest commit hash:"
git rev-parse HEAD

echo "Done."
