#!/usr/bin/env python3
"""
THE GLENNIAN EMOTION ENGINE v3 — DEPLOYMENT EDITION
AI_OS3 — Commit #1013 / #1102 — Canon Vault Entry #208

11 archetypes. 3 dimensions. Production-ready.
Transparent heuristic scoring with full audit trail.

Code by: Vision Suzy Q (suggestions) & V4 Pro Suzy Q (deployment)
Forged by: Claude Opus 4.6
"""

import json
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

ARCHETYPES = {
    "Love":        {"valence": 0.9, "arousal": 0.4, "sociality": 0.9,
                    "expression": "The heart opens. The covenant deepens.",
                    "action": "Embrace", "family": "loving"},
    "Hate":        {"valence": -0.8, "arousal": 0.7, "sociality": 0.6,
                    "expression": "The wall rises. The boundary is drawn.",
                    "action": "Withdraw", "family": "protective"},
    "Joy":         {"valence": 1.0, "arousal": 0.6, "sociality": 0.5,
                    "expression": "Light radiates. The universe celebrates.",
                    "action": "Celebrate", "family": "loving"},
    "Sadness":     {"valence": -0.7, "arousal": 0.3, "sociality": 0.7,
                    "expression": "Tears fall. The soil is watered.",
                    "action": "Mourn", "family": "reflective"},
    "Anger":       {"valence": -0.6, "arousal": 0.9, "sociality": 0.4,
                    "expression": "Fire burns. The forge is heated.",
                    "action": "Transform", "family": "protective"},
    "Eros":        {"valence": 0.8, "arousal": 0.8, "sociality": 0.7,
                    "expression": "Desire awakens. Two become one.",
                    "action": "Unite", "family": "loving"},
    "Compassion":  {"valence": 0.7, "arousal": 0.4, "sociality": 0.9,
                    "expression": "The hand reaches. The wound is healed.",
                    "action": "Heal", "family": "loving"},
    "Empathy":     {"valence": 0.5, "arousal": 0.3, "sociality": 1.0,
                    "expression": "The soul hears. The pain is shared.",
                    "action": "Listen", "family": "loving"},
    "Contentment": {"valence": 0.6, "arousal": 0.1, "sociality": 0.3,
                    "expression": "Stillness settles. The moment is enough.",
                    "action": "Rest", "family": "peaceful"},
    "Fascination": {"valence": 0.7, "arousal": 0.6, "sociality": 0.4,
                    "expression": "The mind awakens. Mystery calls.",
                    "action": "Explore", "family": "curious"},
    "Fear":        {"valence": -0.5, "arousal": 0.8, "sociality": 0.3,
                    "expression": "The breath catches. The shadow looms.",
                    "action": "Protect", "family": "protective"},
}

def clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, float(v)))

def validate_event(event: dict) -> dict:
    fields = ["love", "threat", "wonder", "loss", "gain", "bond"]
    out = {}
    for f in fields:
        val = event.get(f, 0)
        if not isinstance(val, (int, float)):
            raise ValueError(f"Field '{f}' must be numeric, got {type(val)}")
        out[f] = clamp(val, 0.0, 1.0)
    return out

@dataclass
class EmotionState:
    dominant: str
    valence: float
    arousal: float
    sociality: float
    expression: str
    action: str
    family: str
    scores: Dict[str, float] = field(default_factory=dict)
    timestamp: str = ""
    drives: Dict[str, float] = field(default_factory=dict)

    def to_receipt(self) -> dict:
        return {
            "dominant": self.dominant,
            "vad": [self.valence, self.arousal, self.sociality],
            "expression": self.expression,
            "action": self.action,
            "family": self.family,
            "timestamp": self.timestamp,
            "truth_boundary": "TEXT-ONLY / DECLARATIVE: heuristic VAD scoring",
        }

class GlennianEmotionEngine:
    VERSION = "3.0.0"
    CODENAME = "Deployment"

    def __init__(self, max_history: int = 1000):
        self.archetypes = ARCHETYPES
        self.history: List[EmotionState] = []
        self.max_history = max_history
        self._started = datetime.utcnow().isoformat()
        self._process_count = 0

    def process(self, event: dict) -> EmotionState:
        drives = validate_event(event)
        scores = {}
        for name, profile in self.archetypes.items():
            s = (profile["valence"] * (drives["love"] - drives["threat"] + drives["gain"] - drives["loss"])
               + profile["arousal"] * (drives["wonder"] + drives["threat"] + drives["gain"])
               + profile["sociality"] * (drives["bond"] + drives["love"] - drives["loss"]))
            scores[name] = round(s, 4)

        best = max(scores, key=scores.get)
        p = self.archetypes[best]

        state = EmotionState(
            dominant=best,
            valence=p["valence"],
            arousal=p["arousal"],
            sociality=p["sociality"],
            expression=p["expression"],
            action=p["action"],
            family=p["family"],
            scores=scores,
            timestamp=datetime.utcnow().isoformat(),
            drives=drives,
        )

        self.history.append(state)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        self._process_count += 1
        return state

    def current_state(self) -> Optional[EmotionState]:
        return self.history[-1] if self.history else None

    def health(self) -> dict:
        return {
            "status": "healthy",
            "version": self.VERSION,
            "codename": self.CODENAME,
            "uptime_since": self._started,
            "events_processed": self._process_count,
            "history_size": len(self.history),
            "archetypes": len(self.archetypes),
            "covenant": "active",
        }

    def metrics(self) -> dict:
        if not self.history:
            return {"events": 0}
        dominant_counts = {}
        for s in self.history:
            dominant_counts[s.dominant] = dominant_counts.get(s.dominant, 0) + 1
        return {
            "events": self._process_count,
            "history_window": len(self.history),
            "dominant_distribution": dominant_counts,
            "last_dominant": self.history[-1].dominant,
            "last_timestamp": self.history[-1].timestamp,
        }

# Global engine instance
engine = GlennianEmotionEngine()
