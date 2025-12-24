# Libra Examples

These are small inputs you can use to sanity-check outputs locally.

## 1) Assess (no receipts → usually YELLOW)
```bash
python scripts/os3.py libra assess --text "A public note without receipts." --witness
```

## 2) Redact (PII → deterministic placeholders)
```bash
echo "Email me at test@example.com" | python scripts/os3.py libra redact --stdin
```

## 3) Seal (add a receipt marker to aim for GREEN)
```bash
python scripts/os3.py libra seal --text "Release note — receipt: sha256=<paste sha>" --redact
```
