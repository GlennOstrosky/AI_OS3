Title: Install gravity-biased double-slit rule (candidate_rules_gravity)

Summary:
Adds a validated, versioned rule plugin implementing a double-slit simulation with a gentle gravity bias. The plugin is hot-reloadable and intended for local experiments with quantum_world.

Changes:
- candidate_rules_gravity.py — new rule plugin (gravity-biased double-slit)
- tests/test_gravity.py — unit test verifying downward bias behavior
- rules_versions/ — versioned copy of the installed plugin (created by rules_manager.py)
- rules_manifest.json — manifest entry for the installed plugin
- rules_double_slit.py — active plugin replaced with the installed version
- quantum_world.py — minimal simulation module (for tests)

How to run locally:
1. Validate and install locally:
   py -3 rules_manager.py candidate_rules_gravity.py --author "Glenn" || python rules_manager.py candidate_rules_gravity.py --author "Glenn"
2. Run the simulation:
   py -3 quantum_world.py || python quantum_world.py
3. Run tests:
   py -3 -m pytest -q || python -m pytest -q

Notes:
- Validation runs a short sandboxed import and a basic compute_pixel call before installing.
- Keep network_bridge.py off public interfaces; run rule updates locally or in a sandbox.
