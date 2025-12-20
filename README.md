[![os3-verify](https://github.com/GlennOstrosky/AI_OS3/actions/workflows/os3-verify.yml/badge.svg)](https://github.com/GlennOstrosky/AI_OS3/actions/workflows/os3-verify.yml)
### Ledger verification (OS3)

AI_OS3 uses an append-only ledger (`os3/ledger.jsonl`) that records the SHA256 (`sha256`) of each sealed receipt/snapshot file (`path`). Verification is cross-platform via `scripts/verify_snapshot.py`, and CI runs the verifier on every push/PR (see `os3-verify` workflow). This establishes an auditable truth loop: receipt → sha256 → ledger → verifier → CI witness.
