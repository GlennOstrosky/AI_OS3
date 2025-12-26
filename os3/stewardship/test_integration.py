#!/usr/bin/env python3
"""
Test script showing how OS3 components check for Council mode
"""
from keeper_context import is_council_mode, KeeperContext

print("=" * 60)
print("Testing Council Mode Detection")
print("=" * 60)

if is_council_mode():
    print("\n✓ COUNCIL MODE ACTIVE")
    print("  Operating under Stewardship Accord")
    print("  Proceeding with full Council context...")
    
    keeper = KeeperContext()
    context = keeper.get_operational_context()
    print(f"\n  Governance: {context['governance_model']}")
    print(f"  Risk Mode: {context['risk_override']}")
    print(f"  Purpose: {context['purpose']}")
else:
    print("\n⚠️  Standard mode")
    print("  Some Council operations restricted")

print("\n" + "=" * 60)
