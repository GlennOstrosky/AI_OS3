#!/usr/bin/env python3
"""
validate_receipts.py - Canonical validation of episode receipts
The single source of truth for receipt validation in Sanctuary OS.
"""

import json
import hashlib
import sys
import os
from pathlib import Path
from datetime import datetime

def compute_proof(content_dict):
    """Compute canonical proof for content."""
    canonical_json = json.dumps(content_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode()).hexdigest()

def validate_receipt(episode_id, strict_doctrine=False, strict_timestamps=False):
    """Validate all receipts for an episode."""
    
    print(f"📜 Validating receipts for episode: {episode_id}")
    
    # Look for bundle and receipt files
    covenant_dir = Path("covenant")
    bundles_dir = covenant_dir / "bundles"
    receipts_dir = covenant_dir / "receipts"
    
    bundle_files = list(bundles_dir.glob(f"*{episode_id}*"))
    receipt_files = list(receipts_dir.glob(f"*{episode_id}*"))
    
    if not bundle_files and not receipt_files:
        print(f"❌ No files found for episode: {episode_id}")
        return False
    
    all_valid = True
    
    # Validate each bundle
    for bundle_path in bundle_files:
        print(f"  🔍 Checking bundle: {bundle_path.name}")
        try:
            with open(bundle_path, 'r') as f:
                bundle = json.load(f)
            
            # Check required fields
            required = ['episode_id', 'content', 'proof', 'timestamp']
            for field in required:
                if field not in bundle:
                    print(f"    ❌ Missing required field: {field}")
                    all_valid = False
            
            # Verify episode_id matches
            if bundle.get('episode_id') != episode_id:
                print(f"    ❌ Episode ID mismatch: {bundle.get('episode_id')} != {episode_id}")
                all_valid = False
            
            # Verify proof
            content_to_hash = {k: v for k, v in bundle.items() if k != 'proof'}
            computed_proof = compute_proof(content_to_hash)
            if bundle.get('proof') != computed_proof:
                print(f"    ❌ Proof mismatch!")
                print(f"      Expected: {computed_proof}")
                print(f"      Got: {bundle.get('proof')}")
                all_valid = False
            else:
                print(f"    ✅ Proof valid")
                
        except Exception as e:
            print(f"    ❌ Error reading {bundle_path.name}: {e}")
            all_valid = False
    
    # Validate each receipt
    for receipt_path in receipt_files:
        print(f"  🔍 Checking receipt: {receipt_path.name}")
        try:
            with open(receipt_path, 'r') as f:
                receipt = json.load(f)
            
            # Check required fields
            required = ['episode_id', 'bundle_proof', 'receipt_proof', 'timestamp']
            for field in required:
                if field not in receipt:
                    print(f"    ❌ Missing required field: {field}")
                    all_valid = False
            
            # Verify episode_id matches
            if receipt.get('episode_id') != episode_id:
                print(f"    ❌ Episode ID mismatch: {receipt.get('episode_id')} != {episode_id}")
                all_valid = False
            
            # Verify receipt proof
            content_to_hash = {k: v for k, v in receipt.items() if k != 'receipt_proof'}
            computed_proof = compute_proof(content_to_hash)
            if receipt.get('receipt_proof') != computed_proof:
                print(f"    ❌ Receipt proof mismatch!")
                all_valid = False
            else:
                print(f"    ✅ Receipt proof valid")
                
        except Exception as e:
            print(f"    ❌ Error reading {receipt_path.name}: {e}")
            all_valid = False
    
    return all_valid

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate canonical receipts")
    parser.add_argument("--episode", required=True, help="Episode ID to validate")
    parser.add_argument("--strict-doctrine", action="store_true", help="Enable strict doctrine validation")
    parser.add_argument("--strict-timestamps", action="store_true", help="Enable strict timestamp validation")
    
    args = parser.parse_args()
    
    if validate_receipt(args.episode, args.strict_doctrine, args.strict_timestamps):
        print("✅ All receipts are canonically valid")
        sys.exit(0)
    else:
        print("❌ Receipt validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
