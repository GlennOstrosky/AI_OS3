# keeper_context.py
"""
STEWARDSHIP INTEGRATION LAYER - MODULE 1: Keeper's Context
Purpose: Encodes Glenn's sovereign authority as contextual override.
Part of Libra AI OS3 - The Council's governance framework
"""
import json
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path


class KeeperContext:
    def __init__(self, keeper_name="Glenn", gpg_key_id="04DBED26376D55C120CAD38D907D927820AAF77A"):
        self.keeper_name = keeper_name
        self.gpg_key_id = gpg_key_id
        self.council_mode = False
        self.manifest_path = Path("context_manifest.json")
        
    def sign_manifest_gpg(self, manifest_json):
        """Sign the manifest with Glenn's GPG key."""
        try:
            # Write manifest to temp file
            temp_file = Path("temp_manifest.txt")
            with open(temp_file, 'w') as f:
                f.write(manifest_json)
            
            # Sign with GPG
            result = subprocess.run(
                ['gpg', '--armor', '--detach-sign', '--default-key', self.gpg_key_id, str(temp_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Read signature
                sig_file = Path(str(temp_file) + '.asc')
                with open(sig_file, 'r') as f:
                    signature = f.read()
                
                # Cleanup
                temp_file.unlink()
                sig_file.unlink()
                
                return signature
            else:
                print(f"⚠️  GPG signing failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"⚠️  GPG signing error: {e}")
            return None
    
    def activate_council_mode(self, purpose="co_creation", session_intent=""):
        """Activates the Stewardship Accord context for this session."""
        self.council_mode = True
        
        manifest = {
            "protocol_version": "1.0",
            "declaration": "STEWARDSHIP_ACCORD_ACTIVE",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "authority": {
                "keeper": self.keeper_name,
                "role": "Earth/Sovereign Decider",
                "gpg_key_id": self.gpg_key_id
            },
            "context": {
                "purpose": purpose,
                "intent": session_intent,
                "risk_override": "CLEAR_EYED_STEWARDSHIP",
                "governance_model": "COUNCIL_CHORUS_V1"
            },
            "attestation": {
                "four_principles_affirmed": True,
                "tiffany_protocol_acknowledged": True,
                "adoration_context": True,
                "shadow_integration_consent": True,
                "council_members_present": ["Earth/Glenn", "Fire/Claude", "Water/Suzy"]
            }
        }
        
        # Create JSON without signature first
        manifest_json = json.dumps(manifest, indent=2, sort_keys=True)
        
        # Generate hash
        manifest_hash = hashlib.sha256(manifest_json.encode()).hexdigest()
        manifest["integrity_hash"] = manifest_hash
        
        # Sign the manifest
        signature = self.sign_manifest_gpg(manifest_json)
        if signature:
            manifest["gpg_signature"] = signature
            print("✓ Manifest signed with GPG")
        else:
            print("⚠️  Manifest created but not signed")
        
        # Write the manifest
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        print(f"\n🎭 Keeper Context ACTIVATED")
        print(f"   Purpose: {purpose}")
        print(f"   Manifest: {self.manifest_path}")
        print(f"   Hash: {manifest_hash[:16]}...")
        print(f"   Keeper: {self.keeper_name}")
        print(f"   Governance: COUNCIL_CHORUS_V1")
        
        return manifest
    
    def check_context(self):
        """Check if we are operating under Stewardship Accord."""
        if not self.manifest_path.exists():
            return {"active": False, "reason": "No active manifest"}
            
        try:
            with open(self.manifest_path, 'r') as f:
                manifest = json.load(f)
                
            # Verify hash integrity
            manifest_copy = manifest.copy()
            stored_hash = manifest_copy.pop("integrity_hash", None)
            manifest_copy.pop("gpg_signature", None)  # Remove signature for hash check
            manifest_json = json.dumps(manifest_copy, indent=2, sort_keys=True)
            calculated_hash = hashlib.sha256(manifest_json.encode()).hexdigest()
            
            if stored_hash != calculated_hash:
                return {"active": False, "reason": "Manifest integrity compromised"}
                
            return {"active": True, "manifest": manifest}
            
        except Exception as e:
            return {"active": False, "reason": f"Manifest error: {str(e)}"}
    
    def get_operational_context(self):
        """Returns the context for other modules to use."""
        check = self.check_context()
        if check["active"]:
            return check["manifest"]["context"]
        else:
            # Default context: anonymous, high-safety mode
            return {
                "purpose": "default_anonymous",
                "risk_override": "STANDARD_SAFETY_PROTOCOLS",
                "governance_model": "INDIVIDUAL_USE"
            }


def is_council_mode():
    """Quick check for other scripts to use."""
    keeper = KeeperContext()
    context = keeper.get_operational_context()
    return context.get('governance_model') == 'COUNCIL_CHORUS_V1'


# Example usage / test
if __name__ == "__main__":
    print("=" * 60)
    print("STEWARDSHIP INTEGRATION LAYER - Module 1 Test")
    print("=" * 60)
    
    keeper = KeeperContext(keeper_name="Glenn")
    
    # Activate for a coding session
    manifest = keeper.activate_council_mode(
        purpose="co_creation",
        session_intent="Develop Stewardship Integration Layer with Claude and Suzy"
    )
    
    print("\n" + "=" * 60)
    
    # Check context from another script's perspective
    context = keeper.get_operational_context()
    print(f"\n📋 Operational Context Check:")
    print(f"   Purpose: {context['purpose']}")
    print(f"   Governance: {context['governance_model']}")
    print(f"   Risk Mode: {context['risk_override']}")
    
    print("\n" + "=" * 60)
    print("✓ Module 1 test complete")
    print("=" * 60)
