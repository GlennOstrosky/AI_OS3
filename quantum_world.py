#!/usr/bin/env python3
"""
quantum_world.py
Minimal observer-dependent quantum-pixel simulation used by tests.
"""

import importlib.util
import importlib
import random
from pathlib import Path
from typing import Optional, Callable, Dict, Any

PixelValue = Any

class QuantumPixel:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self._computed = False
        self._value: Optional[PixelValue] = None
        self._latent_seed = random.random()

    def is_computed(self) -> bool:
        return self._computed

    def compute(self, rule_fn: Callable[[int,int,'World',Dict], PixelValue], world: 'World', context: Dict) -> PixelValue:
        if not self._computed:
            self._value = rule_fn(self.x, self.y, world, context)
            self._computed = True
        return self._value

    def peek_latent(self) -> float:
        return self._latent_seed

class RuleEngine:
    def __init__(self, module_path: Optional[str] = None):
        self.module_path = module_path
        self.module = None
        if module_path:
            self.load_module(module_path)

    def load_module(self, module_path: str):
        path = Path(module_path)
        if not path.exists():
            self.module = None
            return
        spec = importlib.util.spec_from_file_location("physics_rules", str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        self.module = module

    def reload(self):
        if self.module:
            importlib.reload(self.module)

    def compute_pixel(self, x:int, y:int, world:'World', context:Dict) -> PixelValue:
        if self.module and hasattr(self.module, "compute_pixel"):
            return self.module.compute_pixel(x, y, world, context)
        pixel = world.grid[y][x]
        return 1 if pixel.peek_latent() + random.uniform(-0.1,0.1) > 0.5 else 0

    def on_step(self, world:'World', step:int):
        if self.module and hasattr(self.module, "on_step"):
            return self.module.on_step(world, step)
        return None

class World:
    def __init__(self, width:int, height:int, rules:RuleEngine):
        self.width = width
        self.height = height
        self.rules = rules
        self.grid = [[QuantumPixel(x,y) for x in range(width)] for y in range(height)]
        self.step_count = 0

    def observe(self, x:int, y:int, observer_context:Optional[Dict]=None) -> PixelValue:
        context = observer_context or {"observer": True}
        pixel = self.grid[y][x]
        return pixel.compute(self.rules.compute_pixel, self, context)

    def peek(self, x:int, y:int) -> float:
        return self.grid[y][x].peek_latent()

    def step(self):
        self.step_count += 1
        self.rules.on_step(self, self.step_count)

    def reset(self):
        for row in self.grid:
            for p in row:
                p._computed = False
                p._value = None
                p._latent_seed = random.random()
        self.step_count = 0
