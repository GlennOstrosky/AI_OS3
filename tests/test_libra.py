# tests/test_libra.py
from os3.libra import assess, redact, Verdict


def test_email_triggers_redaction_and_red_or_yellow():
    text = "Contact me at test@example.com and we are confirmed."
    res = assess(text)
    # PII should push to RED (hard)
    assert res.verdict in (Verdict.RED, Verdict.YELLOW)
    redacted, changed, _ = redact(text)
    assert changed is True
    assert "test@example.com" not in redacted
    assert "[REDACTED:EMAIL]" in redacted


def test_receipt_marker_improves_readiness():
    text = "All verifiable. sha256: " + ("a" * 64)
    res = assess(text)
    assert res.verdict in (Verdict.GREEN, Verdict.YELLOW)  # should not be RED
    assert res.score >= 90


def test_abs_solute_without_receipts_yellow():
    text = "This is proven and confirmed and guaranteed."
    res = assess(text)
    assert res.verdict in (Verdict.YELLOW, Verdict.RED)
