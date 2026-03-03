#!/usr/bin/env python3
"""
rules_manager.py
Validate, version, and atomically install rule plugin files for quantum_world.
Minimal, local-only installer used by the run_install_and_test.sh helper.
"""

import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import sys

MANIFEST = Path("rules_manifest.json")
RULES_DIR = Path("rules_versions")
ACTIVE_RULE = Path("rules_double_slit.py")  # active plugin target

RULES_DIR.mkdir(exist_ok=True)

def validate_rules_file(path: Path, timeout: int = 3) -> bool:
    code = f'''
import importlib.util, sys
p = r"{str(path)}"
spec = importlib.util.spec_from_file_location("tmp_rules", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
if not hasattr(m, "compute_pixel"):
    raise SystemExit(2)
res = m.compute_pixel(0,0, None, {{}})
print("OK", type(res))
'''
    try:
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def version_and_install(path: Path, author: str = "agent"):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = RULES_DIR / f"{path.stem}_{ts}{path.suffix}"
    shutil.copy2(path, dest)
    manifest = MANIFEST.exists() and json.loads(MANIFEST.read_text()) or []
    manifest.append({
        "file": str(dest),
        "installed_at": ts,
        "author": author
    })
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    shutil.copy2(dest, ACTIVE_RULE)
    return dest

def install_new_rule(source_path: Path, author: str = "agent"):
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    ok = validate_rules_file(source_path)
    if not ok:
        raise RuntimeError("Validation failed for rules file.")
    return version_and_install(source_path, author)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("file", type=Path, help="New rule file to validate and install")
    p.add_argument("--author", default="agent")
    args = p.parse_args()
    try:
        dest = install_new_rule(args.file, args.author)
        print("Installed:", dest)
    except Exception as e:
        print("Error:", e)
        raise
