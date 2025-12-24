# Libra OS Doctrine (OS3)

## Purpose
Libra OS is a deterministic governance layer for **public readiness**.
It does **not** predict outcomes. It **governs release**:
- Helps separate *private* from *public-ready* content
- Flags missing provenance/receipts
- Redacts obvious PII deterministically
- Produces paste-ready witness blocks (timestamp + sha256 + findings)

## The 7 Pillars
1. **Truth Boundary** - Receipts and SHA256 markers are encouraged for public claims
2. **Consent & Privacy** - Detect common PII patterns (email/phone/SSN/card) and recommend redaction
3. **Clarity** - Findings are phrased as guidance, not condemnation
4. **Reproducibility** - Same input → same output, and hashes allow verification
5. **Non-harm** - Deterministic redaction prevents accidental doxxing or leakage
6. **Tone Balance** - Scoring + thresholds help keep posts steady and responsible
7. **Public Readiness** - Verdicts: GREEN (ready), YELLOW (revise), RED (hold)

## Operational Rules
- Prefer **GREEN** for public posts
- If **YELLOW**, do at least one: add provenance, redact PII, or clarify claims
- If **RED**, do not publish

## Receipts Guidance
A "receipt marker" can be as simple as:
- `receipt: sha256=<64hex>`
- `receipt: os3/receipts/<file>.txt`
- a known ledger/session reference

This is not bureaucracy — it's **trust portability**.

## Commands

### Assess
```bash
python scripts/os3.py libra assess --text "Draft post" --witness
echo "Draft post" | python scripts/os3.py libra assess --stdin --witness
```

### Redact
```bash
echo "Email me at test@example.com" | python scripts/os3.py libra redact --stdin
```

### Seal
```bash
python scripts/os3.py libra seal --text "Public post with receipt: sha256=..." --redact
```

## Council Line

**Libra does not predict; Libra governs.** ⚖️
