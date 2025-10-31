"""
NCRYPT Whitepaper Demo
======================

Demonstrates the key concepts from the NCRYPT whitepaper:
1. Quantum-resistant cryptography (Module-LWE/SIS)
2. Multi-tier privacy (Transparent, Private, Accountable)
3. DAPOA framework
4. Quantum key distribution for secure channels
"""

import logging
from ncrypt.lattice.post_quantum import LatticeCrypto, ModuleLWE, ModuleSIS
from ncrypt.transactions.privacy_modes import (
    DAPOAFramework, PrivacyMode, TransparentTransaction,
    PrivateTransaction, AccountableTransaction
)
from ncrypt.core.qkd import BB84Protocol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_quantum_resistant_encryption():
    """Demonstrate Module-LWE post-quantum encryption."""
    print("\n" + "=" * 70)
    print("1. QUANTUM-RESISTANT ENCRYPTION (Module-LWE)")
    print("=" * 70)
    
    lattice = LatticeCrypto()
    
    # Generate quantum-resistant keypair
    print("\n📡 Generating quantum-resistant keypair using Module-LWE...")
    public_key, private_key = lattice.generate_account_keypair()
    print("✅ Keypair generated (secure against quantum computers)")
    
    # Encrypt a message
    message = b"NCRYPT: Quantum-resistant blockchain platform"
    print(f"\n🔒 Encrypting message: '{message.decode()}'")
    encrypted = lattice.encrypt_message(public_key, message)
    print(f"✅ Message encrypted with {len(encrypted['ciphertexts'])} ciphertexts")
    
    # Decrypt the message
    print("\n🔓 Decrypting message...")
    decrypted = lattice.decrypt_message(private_key, encrypted)
    print(f"✅ Decrypted: '{decrypted.decode()}'")
    
    # Verify
    if message == decrypted:
        print("\n✅ SUCCESS: Quantum-resistant encryption working correctly!")
    
    return lattice


def demo_value_commitments(lattice: LatticeCrypto):
    """Demonstrate Module-SIS commitments for hidden values."""
    print("\n" + "=" * 70)
    print("2. VALUE COMMITMENTS (Module-SIS)")
    print("=" * 70)
    
    amount = 1000  # Transaction amount
    print(f"\n💰 Creating commitment to transaction amount: {amount}")
    
    commitment, opening = lattice.create_value_commitment(amount)
    print(f"✅ Commitment created (hides the amount)")
    print(f"   Commitment size: {len(commitment)} elements")
    
    # Verify commitment
    print(f"\n🔍 Verifying commitment...")
    is_valid = lattice.verify_value_commitment(commitment, amount, opening)
    
    if is_valid:
        print("✅ Commitment verified correctly!")
    else:
        print("❌ Commitment verification failed!")
    
    # Try with wrong amount
    print(f"\n🔍 Attempting verification with wrong amount (500)...")
    is_valid_wrong = lattice.verify_value_commitment(commitment, 500, opening)
    
    if not is_valid_wrong:
        print("✅ Correctly rejected wrong amount!")
    else:
        print("❌ Should have rejected wrong amount!")


def demo_multi_tier_privacy():
    """Demonstrate NCRYPT's three privacy levels."""
    print("\n" + "=" * 70)
    print("3. MULTI-TIER PRIVACY FRAMEWORK")
    print("=" * 70)
    
    dapoa = DAPOAFramework()
    
    # Transparent Mode
    print("\n🔍 TRANSPARENT MODE (Public blockchain)")
    print("   - Addresses visible")
    print("   - Amounts visible")
    print("   - Suitable for: public audits, transparency requirements")
    
    transparent_tx = dapoa.create_transaction(
        privacy_mode=PrivacyMode.TRANSPARENT,
        sender="alice_address_123",
        recipient="bob_address_456",
        amount=100,
        inputs=["input_txo_1"]
    )
    print(f"✅ Created transparent transaction")
    print(f"   Hash: {transparent_tx.compute_hash()[:16]}...")
    print(f"   Recipient: {transparent_tx.outputs[0].address}")
    print(f"   Amount: {transparent_tx.outputs[0].amount}")
    
    # Private Mode
    print("\n🔒 PRIVATE MODE (Maximum anonymity)")
    print("   - Addresses hidden")
    print("   - Amounts hidden")
    print("   - Suitable for: privacy-maximizing users")
    
    private_tx = dapoa.create_transaction(
        privacy_mode=PrivacyMode.PRIVATE,
        sender="alice_address_123",
        recipient="charlie_address_789",
        amount=250,
        inputs=["input_txo_2", "input_txo_3"]
    )
    print(f"✅ Created private transaction")
    print(f"   Hash: {private_tx.compute_hash()[:16]}...")
    print(f"   Recipient: {private_tx.outputs[0].address} (hidden)")
    print(f"   Amount: {private_tx.outputs[0].amount} (hidden)")
    print(f"   Encrypted data: {len(private_tx.outputs[0].encrypted_data)} bytes")
    
    # Accountable Mode
    print("\n🎯 ACCOUNTABLE MODE (Privacy + Compliance)")
    print("   - Addresses hidden (but revealable to auditor)")
    print("   - Amounts hidden (but provable)")
    print("   - Suitable for: institutions, regulated entities")
    
    accountable_tx = dapoa.create_transaction(
        privacy_mode=PrivacyMode.ACCOUNTABLE,
        sender="bank_address_abc",
        recipient="customer_address_def",
        amount=5000,
        inputs=["input_txo_4"],
        tracking_key="auditor_public_key_xyz"
    )
    print(f"✅ Created accountable transaction")
    print(f"   Hash: {accountable_tx.compute_hash()[:16]}...")
    print(f"   Tracking key: {accountable_tx.tracking_key}")
    print(f"   Value commitment: {accountable_tx.outputs[0].commitment[:8].hex()}...")
    
    # Auditor revelation
    print("\n👨‍⚖️ AUDITOR DISCLOSURE")
    print("   Authorized auditor can reveal transaction details...")
    
    revealed = dapoa.reveal_to_auditor(accountable_tx, "auditor_private_key")
    if revealed:
        print(f"✅ Transaction revealed to auditor:")
        print(f"   Sender: {revealed['sender']}")
        print(f"   Recipient: {revealed['recipient']}")
        print(f"   Amount: {revealed['amount']}")
        print(f"\n   ℹ️  Privacy maintained from unauthorized parties!")


def demo_qkd_secure_channel():
    """Demonstrate QKD for establishing secure quantum channel."""
    print("\n" + "=" * 70)
    print("4. QUANTUM KEY DISTRIBUTION (BB84)")
    print("=" * 70)
    print("   Establishing quantum-secure communication channel...")
    
    protocol = BB84Protocol()
    result = protocol.run_protocol(n_bits=500, noise_level=0.01)
    
    if result:
        print(f"\n✅ Quantum channel established!")
        print(f"   Key length: {result.key_length} bits")
        print(f"   Error rate: {result.error_rate:.4f}")
        print(f"   Security: Any eavesdropping would be detected!")
        print(f"\n   ℹ️  This key can be used for secure classical encryption")
    else:
        print("❌ Quantum channel establishment failed (possible eavesdropping detected)")


def main():
    """Run complete NCRYPT whitepaper demonstration."""
    print("\n" + "=" * 70)
    print("NCRYPT WHITEPAPER DEMONSTRATION")
    print("Quantum-Resistant Blockchain with Multi-Tier Privacy")
    print("=" * 70)
    
    print("\nThis demo showcases:")
    print("  1. Post-quantum cryptography (Module-LWE/SIS)")
    print("  2. Value commitments for hidden amounts")
    print("  3. Three-tier privacy framework (Transparent/Private/Accountable)")
    print("  4. Quantum key distribution (BB84)")
    
    # Run demonstrations
    lattice = demo_quantum_resistant_encryption()
    demo_value_commitments(lattice)
    demo_multi_tier_privacy()
    demo_qkd_secure_channel()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
NCRYPT provides a complete solution for the quantum era:

✅ Quantum Resistance:
   - Module-LWE encryption (NIST-recommended)
   - Module-SIS commitments and hashes
   - BB84 quantum key distribution
   - Secure against Shor's and Grover's algorithms

✅ Multi-Tier Privacy:
   - Transparent: Public for compliance needs
   - Private: Maximum anonymity for privacy advocates
   - Accountable: Balanced privacy + regulatory compliance

✅ DAPOA Framework:
   - Decentralized: No trusted third parties
   - Anonymous: Cryptographic privacy guarantees
   - Optional Accountability: Selective disclosure to auditors
   
✅ Future-Proof:
   - No hard forks needed for quantum threats
   - Provable security guarantees
   - Ready for the quantum computing era

NCRYPT: Secure. Private. Accountable. Future-Proof.
    """)
    
    print("=" * 70)
    print("✅ Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()

