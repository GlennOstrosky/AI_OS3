#!/usr/bin/env python3
"""
Create a properly proofed episode for testing the Heartbeat Trilogy.
"""

import json
import hashlib
from datetime import datetime

def compute_proof(content_dict):
    """Compute canonical proof for content."""
    canonical_json = json.dumps(content_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode()).hexdigest()

def create_proper_episode(episode_id):
    """Create bundle and receipt with proper proofs."""
    
    # Create bundle content
    bundle_content = {
        "episode_id": episode_id,
        "content": "This is a properly proofed test episode for the Heartbeat Trilogy",
        "timestamp": "2025-12-16T00:00:00Z"
    }
    
    # Compute bundle proof
    bundle_proof = compute_proof(bundle_content)
    bundle_content["proof"] = bundle_proof
    
    # Create receipt content
    receipt_content = {
        "episode_id": episode_id,
        "bundle_proof": bundle_proof,
        "timestamp": "2025-12-16T00:00:01Z"
    }
    
    # Compute receipt proof
    receipt_proof = compute_proof(receipt_content)
    receipt_content["receipt_proof"] = receipt_proof
    
    return bundle_content, receipt_content

if __name__ == "__main__":
    episode_id = "ep_psalm_os_self_aware_2025_12_16"
    
    bundle, receipt = create_proper_episode(episode_id)
    
    # Save files
    import os
    os.makedirs("covenant/bundles", exist_ok=True)
    os.makedirs("covenant/receipts", exist_ok=True)
    
    bundle_path = f"covenant/bundles/bundle_{episode_id}.json"
    receipt_path = f"covenant/receipts/receipt_{episode_id}.json"
    
    with open(bundle_path, 'w') as f:
        json.dump(bundle, f, indent=2)
    
    with open(receipt_path, 'w') as f:
        json.dump(receipt, f, indent=2)
    
    print(f"✅ Created properly proofed episode:")
    print(f"   Bundle: {bundle_path}")
    print(f"   Receipt: {receipt_path}")
    print(f"   Bundle proof: {bundle['proof'][:16]}...")
    print(f"   Receipt proof: {receipt['receipt_proof'][:16]}...")
