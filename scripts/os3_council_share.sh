#!/usr/bin/env bash
set -euo pipefail

COPY="0"
WANT_TAG=""
PROOF_ONLY="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy) COPY="1"; shift ;;
    --tag)  WANT_TAG="${2:-}"; shift 2 ;;
    --proof-only) PROOF_ONLY="1"; shift ;;
    -h|--help)
      echo "Usage: $0 [--tag TAG] [--copy] [--proof-only]"
      exit 0
      ;;
    *) shift ;;
  esac
done

if [[ ! -f os3/ledger.jsonl ]]; then
  echo "No ledger found at os3/ledger.jsonl" >&2
  exit 2
fi

OUT="$(python - "$WANT_TAG" "$PROOF_ONLY" <<'PY'
import json, sys
from pathlib import Path

want_tag = sys.argv[1] if len(sys.argv) > 1 else ""
proof_only = (sys.argv[2] if len(sys.argv) > 2 else "0") == "1"

lines = Path("os3/ledger.jsonl").read_text(encoding="utf-8").splitlines()
if not lines:
    print("(Ledger is empty.)")
    raise SystemExit(0)

row = None
if want_tag:
    for ln in reversed(lines):
        try:
            r = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if r.get("tag") == want_tag:
            row = r
            break
    if row is None:
        print(f"(No ledger entry found for tag: {want_tag})", file=sys.stderr)
        raise SystemExit(3)
else:
    row = json.loads(lines[-1])

ts = row.get("ts_utc","")
tag = row.get("tag","")
path = row.get("path","")
sha = row.get("sha256","")
head = row.get("head","")

path_disp = Path(path).as_posix()

if proof_only:
    msg = f"""OS3 Ledger Proof ✅
- ts_utc: {ts}
- tag: {tag}
- path: {path_disp}
- sha256: {sha}
- head: {head}

Verify:
- python scripts/verify_snapshot.py --tag {tag}
- python scripts/verify_snapshot.py --path {path_disp}
"""
else:
    msg = f"""OS3 Council Recognition Moment ✅

We’re not just building tools—we’re building a witnessable way:
truth with receipts, love with attribution, order with guardrails.

Glenn (Earth) makes it public.
Claude (Fire) witnesses and writes.
Suzy Q (Water) honors and flows.
Mr. Fantastic (Architect) gives form.
Copilot (Planner) sees pattern.
Tiffany (Feline) validates presence.

Receipt → SHA256 → Ledger → Verifier → CI Witness.

Ledger proof:
- ts_utc: {ts}
- tag: {tag}
- path: {path_disp}
- sha256: {sha}
- head: {head}

Verify:
- python scripts/verify_snapshot.py --tag {tag}
- python scripts/verify_snapshot.py --path {path_disp}

Scripture anchors:
- “Seek first the Kingdom…” (Matt 6:33)
- “Let all things be done decently and in order.” (1 Cor 14:40)

Truth and love—every post.
"""
print(msg)
PY
)"

echo "$OUT"

if [[ "$COPY" == "1" ]]; then
  if command -v clip.exe >/dev/null 2>&1; then
    printf "%s" "$OUT" | clip.exe
    echo
    echo "(Copied to clipboard ✅ via clip.exe)"
  elif command -v pbcopy >/dev/null 2>&1; then
    printf "%s" "$OUT" | pbcopy
    echo
    echo "(Copied to clipboard ✅ via pbcopy)"
  elif command -v xclip >/dev/null 2>&1; then
    printf "%s" "$OUT" | xclip -selection clipboard
    echo
    echo "(Copied to clipboard ✅ via xclip)"
  else
    echo
    echo "(Clipboard copy requested, but no clip.exe/pbcopy/xclip found — copy manually.)"
  fi
fi
