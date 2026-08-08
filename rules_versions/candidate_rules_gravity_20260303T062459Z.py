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
