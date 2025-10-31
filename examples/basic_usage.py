"""
Basic usage example of nCrypt SDK.

This example demonstrates:
1. Generating a quantum key using BB84 protocol
2. Encrypting data with the quantum key
3. Decrypting data with the quantum key
"""

import logging
from ncrypt.core.qkd import BB84Protocol
from ncrypt.core.encryption import QuantumEncryption
from ncrypt.utils.key_manager import KeyManager

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    print("=" * 60)
    print("nCrypt: Quantum Cryptography Demo")
    print("=" * 60)
    
    # Step 1: Generate quantum key using BB84 protocol
    print("\n1. Generating quantum key using BB84 protocol...")
    protocol = BB84Protocol(error_threshold=0.11)
    result = protocol.run_protocol(
        n_bits=2000,           # Exchange 2000 qubits
        noise_level=0.01,      # 1% channel noise
        check_sample_ratio=0.5 # Use 50% for error checking
    )
    
    if result is None:
        print("❌ Key generation failed!")
        return
    
    print(f"✅ Quantum key generated!")
    print(f"   Final key length: {result.key_length} bits")
    print(f"   Error rate: {result.error_rate:.4f}")
    print(f"   Efficiency: {result.key_length / (result.key_length + result.discarded_bits):.2%}")
    
    # Step 2: Save the key
    print("\n2. Saving quantum key...")
    key_manager = KeyManager(storage_dir="./demo_keys")
    key_id = "demo_key_001"
    key_manager.save_key(
        result.final_key,
        key_id,
        metadata={
            "protocol": "BB84",
            "noise_level": 0.01,
            "error_rate": result.error_rate
        }
    )
    print(f"✅ Key saved with ID: {key_id}")
    
    # Step 3: Encrypt data
    print("\n3. Encrypting data...")
    plaintext = b"This is a secret message protected by quantum cryptography!"
    print(f"   Plaintext: {plaintext.decode()}")
    
    qe = QuantumEncryption()
    ciphertext, iv, tag = qe.encrypt(plaintext, result.final_key)
    print(f"✅ Data encrypted!")
    print(f"   Ciphertext length: {len(ciphertext)} bytes")
    
    # Step 4: Decrypt data
    print("\n4. Decrypting data...")
    decrypted = qe.decrypt(ciphertext, iv, tag, result.final_key)
    print(f"✅ Data decrypted!")
    print(f"   Decrypted text: {decrypted.decode()}")
    
    # Verify
    if plaintext == decrypted:
        print("\n✅ SUCCESS: Plaintext matches decrypted data!")
    else:
        print("\n❌ ERROR: Decryption failed!")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

