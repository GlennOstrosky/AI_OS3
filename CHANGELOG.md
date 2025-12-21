# CHANGELOG

All notable changes to AI_OS3 are documented in this file.

## [Unreleased]
- Guard v2: Doctor treats rc=9 as BLOCKED; nonzero as ERROR; zero as PASS.
- Path normalization: logs and printed paths use forward slashes.
- Council update post: scripts/os3_council_update_post.sh prints All-Green block, appends proof, supports --tag and --copy.
- Proof-only mode: scripts/os3_council_share.sh --proof-only returns tight proof block (ts_utc, tag, path, sha256, head).
- os3post function: runtime tag resolution reads latest tag from os3/ledger.jsonl and runs the post reliably.
- .gitignore hygiene and README Quickstart added.

## [2025-12-20] — v0.2.0
### Added
- scripts/os3_doctor.sh — one-command sanity check and preview.
- scripts/os3_council_share.sh --proof-only — reproducible proof block output.
- scripts/os3_council_update_post.sh — All-Green post generator with --tag and --copy.
- os3/canon/ — non-executable witness files (psalms and README).

### Fixed
- Guard window enforcement to block rapid reruns.
- Tag handling and latest-tag lookup in post scripts.
- Cross-platform clipboard support (clip.exe fallback for Git Bash).

### Notes
- See README.md Quickstart for the three core commands to reproduce the witness.

## [2025-12-18] — v0.1.0
### Added
- Initial ceremony tooling: receipts, ledger, verifier, and example psalm.
- tools/psalm_embed.py to compute poem SHA256 and extract code blocks.
- scripts/seal_os3_anchor.sh to create annotated git tag and session record.

### Security
- Ledger uses SHA256 as canonical file hash.
