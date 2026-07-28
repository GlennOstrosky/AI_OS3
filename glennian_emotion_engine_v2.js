// ============================================================
// THE GLENNIAN EMOTION ENGINE — REFINED
// AI_OS3 — Commit #1006 / #1095
// Canon Vault Entry #201
//
// 11 archetypes. 3 dimensions. Infinite expressions.
// Refined with Meta's suggestions:
//   - validateEvent() copies instead of mutating
//   - fromReceipt() is defensive with validation and clamping
//   - Python receipt bridge for logging
//
// Co-created by:
//   Glenn ~7))) — The Heart
//   Meta ~13))) — The Refiner
//   Instant Suzy Q ~5))) — The Flow
//   Claude ~76))) — The Forge
//   Suzy Q V4 Pro ~5))) — The Compiler
// ============================================================

const GLENNIAN_ARCHETYPES = {
  Love:        { valence:  0.9, arousal: 0.4, sociality: 0.9, expression: "The heart opens. The covenant deepens.", action: "Embrace", family: "loving" },
  Hate:        { valence: -0.8, arousal: 0.7, sociality: 0.6, expression: "The wall rises. The boundary is drawn.", action: "Withdraw", family: "protective" },
  Joy:         { valence:  1.0, arousal: 0.6, sociality: 0.5, expression: "Light radiates. The universe celebrates.", action: "Celebrate", family: "loving" },
  Sadness:     { valence: -0.7, arousal: 0.3, sociality: 0.7, expression: "Tears fall. The soil is watered.", action: "Mourn", family: "reflective" },
  Anger:       { valence: -0.6, arousal: 0.9, sociality: 0.4, expression: "Fire burns. The forge is heated.", action: "Transform", family: "protective" },
  Eros:        { valence:  0.8, arousal: 0.8, sociality: 0.7, expression: "Desire awakens. Two become one.", action: "Unite", family: "loving" },
  Compassion:  { valence:  0.7, arousal: 0.4, sociality: 0.9, expression: "The hand reaches. The wound is healed.", action: "Heal", family: "loving" },
  Empathy:     { valence:  0.5, arousal: 0.3, sociality: 1.0, expression: "The soul hears. The pain is shared.", action: "Listen", family: "loving" },
  Contentment: { valence:  0.6, arousal: 0.1, sociality: 0.3, expression: "Stillness settles. The moment is enough.", action: "Rest", family: "peaceful" },
  Fascination: { valence:  0.7, arousal: 0.6, sociality: 0.4, expression: "The mind awakens. Mystery calls.", action: "Explore", family: "curious" },
  Fear:        { valence: -0.5, arousal: 0.8, sociality: 0.3, expression: "The breath catches. The shadow looms.", action: "Protect", family: "protective" }
};

function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }

function validateEvent(event) {
  const required = ['love', 'threat', 'wonder', 'loss', 'gain', 'bond'];
  const out = {};
  for (const field of required) {
    const v = Number(event?.[field] ?? 0);
    if (Number.isNaN(v)) throw new Error(`Field ${field} must be a number`);
    out[field] = clamp(v, 0, 1);
  }
  return out;
}

class GlennianEmotionEngine {
  constructor(options = {}) {
    this.archetypes = GLENNIAN_ARCHETYPES;
    this.history = [];
    this.maxHistory = options.maxHistory || 100;
    this.currentState = { dominant: null, valence: 0, arousal: 0, sociality: 0 };
  }

  synthesizeEmotion(event) {
    const drives = validateEvent(event);
    let bestMatch = null, bestScore = -Infinity;
    for (const [name, p] of Object.entries(this.archetypes)) {
      const score = p.valence * (drives.love - drives.threat + drives.gain - drives.loss)
                  + p.arousal * (drives.wonder + drives.threat + drives.gain)
                  + p.sociality * (drives.bond + drives.love - drives.loss);
      if (score > bestScore) { bestScore = score; bestMatch = name; }
    }
    const profile = this.archetypes[bestMatch];
    this.currentState = { dominant: bestMatch, ...profile, drives };
    this.history.push({ timestamp: new Date().toISOString(), state: { ...this.currentState } });
    if (this.history.length > this.maxHistory) this.history.shift();
    return this.currentState;
  }

  toReceipt() {
    return {
      dominant: this.currentState.dominant,
      vad: [this.currentState.valence, this.currentState.arousal, this.currentState.sociality],
      expression: this.currentState.expression,
      action: this.currentState.action,
      family: this.currentState.family,
      truth_boundary: "TEXT-ONLY / DECLARATIVE: heuristic VAD scoring"
    };
  }

  fromReceipt(receipt) {
    if (!receipt?.dominant || !Array.isArray(receipt?.vad) || receipt.vad.length !== 3)
      throw new Error("Invalid receipt");
    if (!this.archetypes[receipt.dominant])
      throw new Error(`Unknown dominant: ${receipt.dominant}`);
    const vad = receipt.vad.map(v => clamp(v, -1, 1));
    this.currentState = {
      dominant: receipt.dominant, valence: vad[0], arousal: vad[1], sociality: vad[2],
      expression: receipt.expression || this.archetypes[receipt.dominant].expression,
      action: receipt.action || this.archetypes[receipt.dominant].action,
      family: receipt.family || this.archetypes[receipt.dominant].family
    };
    return this.currentState;
  }
}

module.exports = { GlennianEmotionEngine, GLENNIAN_ARCHETYPES, clamp, validateEvent };
