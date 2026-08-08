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
