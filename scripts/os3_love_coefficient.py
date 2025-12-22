
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def tokenize(text: str) -> list[str]:
    return [t.strip(".,!?;:\"'()[]{}").lower() for t in text.split() if t.strip()]


def count_matches(tokens: list[str], vocab: set[str]) -> int:
    return sum(1 for t in tokens if t in vocab)


# Transparent lexicon buckets (edit these words anytime)
AFFECTION_WORDS = {"love", "beloved", "care", "warm", "kind"}
GRATITUDE_WORDS = {"thank", "grateful", "appreciate", "blessed"}
TRUST_WORDS = {"trust", "safe", "steady", "truth"}
REPAIR_WORDS = {"sorry", "forgive", "repair", "restore"}


@dataclass(frozen=True)
class LoveCoefficient:
    score: float
    counts: Dict[str, int]
    tokens: int
    notes: str


def compute_love_coefficient(text: str) -> LoveCoefficient:
    """
    Truth boundary:
    - Input: user-declared text only.
    - Output: transparent lexicon counts + normalized score.
    - No sensing. No telemetry. No inference of system state. No mind-reading.
    """
    tokens = tokenize(text)
    token_count = len(tokens)

    affection = count_matches(tokens, AFFECTION_WORDS)
    gratitude = count_matches(tokens, GRATITUDE_WORDS)
    trust = count_matches(tokens, TRUST_WORDS)
    repair = count_matches(tokens, REPAIR_WORDS)

    # Simple weighted score (all weights = 1.0)
    raw = float(affection + gratitude + trust + repair)

    divisor = max(float(token_count), 1.0)  # avoid divide-by-zero
    normalized = raw / divisor

    # clamp to [0, 1]
    score = max(0.0, min(1.0, normalized))

    counts = {
        "affection": affection,
        "gratitude": gratitude,
        "trust": trust,
        "repair": repair,
    }

    return LoveCoefficient(
        score=score,
        counts=counts,
        tokens=token_count,
        notes="Transparent lexicon score (counts + clamp).",
    )


def lc_as_dict(lc: LoveCoefficient) -> Dict[str, Any]:
    return {"score": lc.score, "counts": dict(lc.counts), "tokens": lc.tokens, "notes": lc.notes}


def write_receipt(root: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    receipts_dir = root / "os3" / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)

    utc = utc_now_iso()
    payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    receipt_hash = sha256_text(payload_json)

    receipt = {
        "utc": utc,
        "event_type": "LOVE_COEFFICIENT",
        "payload": payload,
        "receipt_hash": receipt_hash,
    }

    out_path = receipts_dir / f"love_coefficient_{utc.replace(':','')}.json"
    out_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # include where it was written (helpful for Glenn)
    receipt["_receipt_path"] = out_path.as_posix()
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(prog="os3_love_coefficient")
    ap.add_argument("--text", required=True, help="Text to analyze")
    ap.add_argument("--witness", action="store_true", help="Print truth boundary (to stderr)")
    ap.add_argument("--no-receipt", action="store_true", help="Do not write a receipt file")
    args = ap.parse_args()

    text = args.text
    lc = compute_love_coefficient(text)
    payload = lc_as_dict(lc)

    # Witness text goes to stderr so stdout stays clean JSON
    if args.witness:
        sys.stderr.write("TRUTH BOUNDARY:\n")
        sys.stderr.write("Lexicon-based love coefficient computation.\n")
        sys.stderr.write("No sensing. No inference of system state. No mind-reading.\n\n")

    root = Path(".").resolve()

    if args.no_receipt:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return 0

    receipt = write_receipt(root, payload)
    sys.stdout.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


