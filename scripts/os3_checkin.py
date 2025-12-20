from __future__ import annotations
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def sh(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()

def main() -> int:
    print("==============================================")
    print("OS3 CHECK-IN", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    print("==============================================\n")

    print("📋 Git Status:")
    print(sh("git", "status"), "\n")

    print("📚 Recent Commits (last 5):")
    print(sh("git", "log", "--oneline", "-5"), "\n")

    print("🏷️  OS3 Tags (first ceremony):")
    try:
        print(sh("git", "tag", "-n"), "\n")
    except Exception as e:
        print("Tag check failed:", e, "\n")

    latest = None
    sessions = sorted(Path("os3/sessions").glob("*.session.yaml"), key=lambda p: p.stat().st_mtime, reverse=True)
    if sessions:
        latest = sessions[0]

    print("🔍 Latest Session Verification:")
    if latest and Path("scripts/os3_verify_session.py").exists():
        print("Verifying:", latest.as_posix())
        out = sh("py", "scripts/os3_verify_session.py", "--session", str(latest))
        print(out, "\n")
    else:
        print("No session verifier or session files found.\n")

    print("📊 Status File:")
    p = Path("os3_status.json")
    if p.exists():
        print(f"{p}  ({p.stat().st_size} bytes)")
    else:
        print("os3_status.json not found (run: py scripts/os3_status.py --format json > os3_status.json)")

    print("\nOS3 covenant health check complete.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
