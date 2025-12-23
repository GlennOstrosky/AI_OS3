# os3/libra.py
from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Iterable, List, Optional, Tuple


class Verdict(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str  # "info" | "warn" | "red"
    message: str
    suggestion: Optional[str] = None


@dataclass(frozen=True)
class AssessResult:
    verdict: Verdict
    score: int  # higher is better
    findings: Tuple[Finding, ...]
    redaction_needed: bool

    def to_json(self) -> str:
        payload = {
            "verdict": self.verdict.value,
            "score": self.score,
            "redaction_needed": self.redaction_needed,
            "findings": [dataclasses.asdict(f) for f in self.findings],
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    def to_text(self) -> str:
        lines: List[str] = []
        lines.append("╭──────────────────────────────────────────╮")
        lines.append("│ OS3 LIBRA — Balance & Public Readiness   │")
        lines.append("│ Deterministic checks. No sensing.        │")
        lines.append("╰──────────────────────────────────────────╯")
        lines.append(f"Verdict: {self.verdict.value}")
        lines.append(f"Score:   {self.score}")
        lines.append(f"Redact:  {'YES' if self.redaction_needed else 'NO'}")
        lines.append("")
        if not self.findings:
            lines.append("Findings: (none)")
            return "\n".join(lines)

        lines.append("Findings:")
        for f in self.findings:
            badge = {"info": "·", "warn": "!", "red": "X"}.get(f.severity, "·")
            lines.append(f"  {badge} [{f.code}] {f.message}")
            if f.suggestion:
                lines.append(f"      → {f.suggestion}")
        return "\n".join(lines)

    def exit_code(self, strict: bool = False) -> int:
        # Suggested stable exit codes for scripts/CI-ish usage:
        # GREEN=0, YELLOW=2 (or 1 if strict), RED=3
        if self.verdict == Verdict.GREEN:
            return 0
        if self.verdict == Verdict.YELLOW:
            return 1 if strict else 2
        return 3


# ----------------------------
# Deterministic pattern rules
# ----------------------------

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)

# North America-ish phone patterns (broad, deterministic)
PHONE_RE = re.compile(
    r"""
    (?:
        (?:\+?\d{1,3}[\s\-\.])?      # country
        (?:\(?\d{3}\)?[\s\-\.])      # area
        \d{3}[\s\-\.]?\d{4}          # local
    )
    """,
    re.VERBOSE,
)

IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
MAC_RE = re.compile(r"\b(?:[0-9A-F]{2}:){5}[0-9A-F]{2}\b", re.IGNORECASE)

# 64-hex SHA256 (receipt presence)
SHA256_RE = re.compile(r"\b[a-f0-9]{64}\b", re.IGNORECASE)

# “Absolute certainty” language: allowed, but if *no receipts*, it’s a yellow flag for public posts.
ABSOLUTE_WORDS = (
    "proven",
    "proof",
    "confirmed",
    "guaranteed",
    "100%",
    "never",
    "always",
    "undeniable",
    "certain",
)

# “Private/intimate” words are not forbidden, but are a prompt to review for public safety.
INTIMACY_HINTS = (
    "intimate",
    "bedroom",
    "nude",
    "nsfw",
    "explicit",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def redact(text: str) -> Tuple[str, bool, Tuple[Finding, ...]]:
    findings: List[Finding] = []
    changed = False

    def sub(pattern: re.Pattern, repl: str, code: str, msg: str) -> None:
        nonlocal text, changed, findings
        if pattern.search(text):
            text2 = pattern.sub(repl, text)
            if text2 != text:
                changed = True
                text = text2
            findings.append(
                Finding(
                    code=code,
                    severity="warn",
                    message=msg,
                    suggestion="Use the redacted version for any public post.",
                )
            )

    sub(EMAIL_RE, "[REDACTED:EMAIL]", "PII_EMAIL", "Email detected (PII).")
    sub(PHONE_RE, "[REDACTED:PHONE]", "PII_PHONE", "Phone-like number detected (PII).")
    sub(IPV4_RE, "[REDACTED:IPV4]", "PII_IPV4", "IP address detected (PII/telemetry).")
    sub(MAC_RE, "[REDACTED:MAC]", "PII_MAC", "MAC address detected (PII/telemetry).")

    return text, changed, tuple(findings)


def assess(text: str) -> AssessResult:
    findings: List[Finding] = []
    score = 100
    redaction_needed = False

    # PII checks (hard red if present)
    pii_hits = []
    if EMAIL_RE.search(text):
        pii_hits.append("email")
    if PHONE_RE.search(text):
        pii_hits.append("phone")
    if IPV4_RE.search(text):
        pii_hits.append("ipv4")
    if MAC_RE.search(text):
        pii_hits.append("mac")

    if pii_hits:
        score -= 60
        redaction_needed = True
        findings.append(
            Finding(
                code="PII_DETECTED",
                severity="red",
                message=f"Personal/telemetry identifiers detected: {', '.join(sorted(set(pii_hits)))}.",
                suggestion="Run `os3 libra redact` before posting publicly.",
            )
        )

    # Receipts / reproducibility
    has_sha = bool(SHA256_RE.search(text))
    has_receipt_words = any(w in text.lower() for w in ("sha256", "receipt", "sealed", "ledger", "tag"))
    if has_sha or has_receipt_words:
        findings.append(
            Finding(
                code="RECEIPTS_PRESENT",
                severity="info",
                message="Receipt/provenance markers detected (sha/receipt/seal/ledger/tag).",
            )
        )
        score += 5
    else:
        score -= 10
        findings.append(
            Finding(
                code="RECEIPTS_MISSING",
                severity="warn",
                message="No receipt/provenance markers found.",
                suggestion="For public posts, include at least one SHA256 or a receipt line.",
            )
        )

    # Absolute certainty language without receipts => yellow-ish
    abs_hits = [w for w in ABSOLUTE_WORDS if w in text.lower()]
    if abs_hits and not (has_sha or has_receipt_words):
        score -= 15
        findings.append(
            Finding(
                code="ABSOLUTE_NO_RECEIPT",
                severity="warn",
                message=f"High-certainty wording without receipts: {', '.join(abs_hits[:6])}{'...' if len(abs_hits) > 6 else ''}",
                suggestion="Either add receipts (sha/ledger) or soften claims to what’s verifiable.",
            )
        )

    # Intimacy hint: review for public safety (not a ban)
    int_hits = [w for w in INTIMACY_HINTS if w in text.lower()]
    if int_hits:
        score -= 5
        findings.append(
            Finding(
                code="INTIMACY_REVIEW",
                severity="warn",
                message=f"Intimacy hints present: {', '.join(int_hits)}.",
                suggestion="If posting publicly, consider redaction or moving details to the private vault.",
            )
        )

    # Verdict logic (simple, deterministic)
    if any(f.severity == "red" for f in findings):
        verdict = Verdict.RED
    else:
        # If any warnings that matter for public readiness => YELLOW
        warn_codes = {f.code for f in findings if f.severity == "warn"}
        if "PII_DETECTED" in warn_codes or "RECEIPTS_MISSING" in warn_codes or "ABSOLUTE_NO_RECEIPT" in warn_codes:
            verdict = Verdict.YELLOW
        else:
            verdict = Verdict.GREEN

    # Clamp score
    if score < 0:
        score = 0
    if score > 110:
        score = 110

    return AssessResult(verdict=verdict, score=score, findings=tuple(findings), redaction_needed=redaction_needed)


def witness_block(text: str, result: AssessResult, redacted: Optional[str] = None) -> str:
    """
    Paste-ready block for sharing. Deterministic: based only on the provided text/result.
    """
    base_sha = sha256_text(text)
    ts = _utc_now_iso()

    lines: List[str] = []
    lines.append("╭──────────────────────────────────────────╮")
    lines.append("│ OS3 LIBRA WITNESS                         │")
    lines.append("│ Balance verdict + receipt                 │")
    lines.append("╰──────────────────────────────────────────╯")
    lines.append(f"sealed_at: {ts}")
    lines.append(f"verdict:   {result.verdict.value}")
    lines.append(f"score:     {result.score}")
    lines.append(f"sha256:    {base_sha}")

    if redacted is not None and redacted != text:
        lines.append(f"redacted_sha256: {sha256_text(redacted)}")
        lines.append("note: Redacted text differs (PII removed).")

    # Include up to 6 findings lines, short
    important = [f for f in result.findings if f.severity in ("red", "warn")]
    if important:
        lines.append("findings:")
        for f in important[:6]:
            lines.append(f"  - {f.code}: {f.message}")

    return "\n".join(lines)
