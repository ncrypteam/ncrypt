#!/usr/bin/env python3
"""
Quantum vs Classical Demo for Fresh Graduates
==============================================

This demo shows WHEN quantum computing is used in nCrypt:
- Quantum: Key generation (BB84 protocol)
- Classical: Encryption/Decryption (AES-256)
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ncrypt.core.qkd import BB84Protocol
from ncrypt.core.encryption import QuantumEncryption


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_quantum_key_generation():
    """Demonstrate quantum key generation (USES QUANTUM)."""
    print_section("🌀 PART 1: QUANTUM KEY GENERATION (BB84 Protocol)")
    
    print("📚 What's happening:")
    print("   • Alice prepares qubits in QUANTUM SUPERPOSITION states")
    print("   • Bob measures qubits using quantum mechanics")
    print("   • They use the BB84 protocol for quantum key distribution")
    print("   • This part REQUIRES a quantum computer (or simulator)\n")
    
    # Create BB84 protocol instance
    protocol = BB84Protocol(error_threshold=0.11)
    
    print("⚛️  Step 1: Alice generates random bits and bases...")
    print("   Example: bit=1, basis=diagonal → prepares qubit in |−⟩ state")
    
    print("\n⚛️  Step 2: Qubits transmitted through quantum channel...")
    print("   Quantum superposition maintained during transmission")
    
    print("\n⚛️  Step 3: Bob measures qubits in random bases...")
    print("   Quantum measurement COLLAPSES the superposition")
    
    print("\n⚛️  Step 4: Running complete BB84 protocol...")
    start_time = time.time()
    result = protocol.run_protocol(n_bits=2000, noise_level=0.02)
    quantum_time = time.time() - start_time
    
    if result:
        print(f"\n✅ Quantum key generated successfully!")
        print(f"   • Started with: 2000 qubits (quantum operations)")
        print(f"   • Sifted to: {len(result.sifted_key)} bits (bases matched)")
        print(f"   • Final key: {result.key_length} bits (after privacy amplification)")
        print(f"   • Error rate: {result.error_rate:.2%} (quantum noise)")
        print(f"   • Time: {quantum_time:.3f} seconds")
        print(f"\n   💰 On real quantum hardware: ~$38 for IonQ, ~$30 for Rigetti")
        print(f"   ⚠️  This simulator is FREE but not quantum-secure")
        
        return result.final_key
    else:
        print("❌ Key generation failed (error rate too high)")
        return None


def demo_classical_encryption(quantum_key):
    """Demonstrate classical encryption (NO QUANTUM)."""
    print_section("💻 PART 2: CLASSICAL ENCRYPTION (AES-256-GCM)")
    
    print("📚 What's happening:")
    print("   • Using the quantum key for CLASSICAL encryption")
    print("   • AES-256 runs on your regular CPU (no quantum needed)")
    print("   • This is FAST and FREE")
    print("   • Same encryption as banks, messaging apps use\n")
    
    # Create encryption instance
    qe = QuantumEncryption()
    
    # Test message
    plaintext = b"Hello from the quantum world! This message is encrypted with a quantum-generated key, but the encryption itself is classical AES-256."
    
    print(f"📝 Original message ({len(plaintext)} bytes):")
    print(f'   "{plaintext.decode()}"')
    
    # Encrypt
    print("\n🔒 Encrypting with AES-256-GCM (CLASSICAL)...")
    start_time = time.time()
    ciphertext, iv, tag = qe.encrypt(plaintext, quantum_key)
    encrypt_time = time.time() - start_time
    
    print(f"\n✅ Encrypted successfully!")
    print(f"   • Algorithm: AES-256-GCM (classical, not quantum)")
    print(f"   • Ciphertext: {ciphertext[:40].hex()}... ({len(ciphertext)} bytes)")
    print(f"   • Time: {encrypt_time:.6f} seconds")
    print(f"   • Cost: FREE (runs on your CPU)")
    
    # Decrypt
    print("\n🔓 Decrypting (also CLASSICAL)...")
    start_time = time.time()
    decrypted = qe.decrypt(ciphertext, iv, tag, quantum_key)
    decrypt_time = time.time() - start_time
    
    print(f"\n✅ Decrypted successfully!")
    print(f'   "{decrypted.decode()}"')
    print(f"   • Time: {decrypt_time:.6f} seconds")
    print(f"   • Matches original: {decrypted == plaintext}")
    
    return encrypt_time, decrypt_time


def show_comparison():
    """Show side-by-side comparison."""
    print_section("📊 QUANTUM vs CLASSICAL COMPARISON")
    
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│                    KEY GENERATION                           │")
    print("├─────────────────────────────────────────────────────────────┤")
    print("│  ⚛️  QUANTUM COMPUTING REQUIRED                             │")
    print("│  • Prepares qubits in superposition                        │")
    print("│  • Measures quantum states                                 │")
    print("│  • BB84 quantum key distribution protocol                  │")
    print("│  • Needs: AWS Braket, IonQ, Rigetti, or quantum simulator │")
    print("│  • Speed: Slower (quantum operations)                      │")
    print("│  • Cost: $30-38 per key (real hardware)                    │")
    print("│  • Security: Quantum mechanics guarantees                  │")
    print("└─────────────────────────────────────────────────────────────┘")
    print()
    print("                         ⬇️  Produces ⬇️")
    print()
    print("                    [Quantum-Generated Key]")
    print("                 (Stored locally, used many times)")
    print()
    print("                         ⬇️  Used by ⬇️")
    print()
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│                  ENCRYPTION/DECRYPTION                      │")
    print("├─────────────────────────────────────────────────────────────┤")
    print("│  💻 NO QUANTUM COMPUTING NEEDED                             │")
    print("│  • Standard AES-256-GCM encryption                         │")
    print("│  • Runs on regular CPU (classical computing)               │")
    print("│  • Boolean logic and XOR operations                        │")
    print("│  • Needs: Any computer (laptop, server, phone)             │")
    print("│  • Speed: Very fast (millions of bytes/sec)                │")
    print("│  • Cost: FREE (no quantum hardware)                        │")
    print("│  • Security: Quantum key + classical algorithm = secure   │")
    print("└─────────────────────────────────────────────────────────────┘")


def show_real_world_example():
    """Show a real-world usage scenario."""
    print_section("🎯 REAL-WORLD EXAMPLE")
    
    print("Scenario: Company needs to encrypt sensitive data\n")
    
    print("STEP 1: Generate quantum key (ONE TIME)")
    print("─" * 60)
    print("$ ncrypt generate-key --bits 2000 --key-id company_key \\")
    print("         --device braket --backend ionq")
    print()
    print("⚛️  Connecting to IonQ quantum computer...")
    print("⚛️  Running 2000 quantum circuits (BB84 protocol)...")
    print("⚛️  Measuring qubits...")
    print("📊 Sifting keys...")
    print("🔐 Privacy amplification...")
    print("✅ Key generated: 700 bits")
    print("💰 Cost: $38.00 (quantum hardware usage)")
    print("💾 Saved to: keys/company_key.json")
    print()
    
    print("STEP 2: Encrypt files (UNLIMITED TIMES, FREE)")
    print("─" * 60)
    print("$ ncrypt encrypt payroll_2024.xlsx --key-id company_key")
    print("✅ Encrypted in 0.003 seconds (FREE)")
    print()
    print("$ ncrypt encrypt customer_db.sql --key-id company_key")
    print("✅ Encrypted in 0.156 seconds (FREE)")
    print()
    print("$ ncrypt encrypt financial_report.pdf --key-id company_key")
    print("✅ Encrypted in 0.012 seconds (FREE)")
    print()
    print("... encrypt as many files as you want with the same quantum key!")
    print()
    
    print("💡 Key Insight:")
    print("   • Quantum: Used ONCE for key generation ($38)")
    print("   • Classical: Used MANY TIMES for encryption (FREE)")
    print("   • One quantum key → Encrypt unlimited files")


def main():
    """Run the complete demo."""
    print("\n" + "="*70)
    print("  QUANTUM vs CLASSICAL: When Does nCrypt Use Quantum Computing?")
    print("  Demo for Fresh Graduates")
    print("="*70)
    
    print("\n🎓 Learning Objectives:")
    print("   1. Understand that quantum is used for KEY GENERATION")
    print("   2. Understand that classical is used for ENCRYPTION")
    print("   3. See the hybrid approach in action")
    
    # Part 1: Quantum key generation
    quantum_key = demo_quantum_key_generation()
    
    if quantum_key is None:
        print("\n❌ Demo failed - couldn't generate key")
        return
    
    # Part 2: Classical encryption
    encrypt_time, decrypt_time = demo_classical_encryption(quantum_key)
    
    # Show comparison
    show_comparison()
    
    # Show real-world example
    show_real_world_example()
    
    # Summary
    print_section("🎓 SUMMARY FOR FRESH GRADUATES")
    
    print("Key Takeaways:")
    print()
    print("1️⃣  QUANTUM COMPUTING is used for:")
    print("   ✓ Generating cryptographic keys (BB84 protocol)")
    print("   ✓ Creating quantum-secure random numbers")
    print("   ✓ Exploiting quantum mechanics for security")
    print("   ✗ NOT for encrypting your actual data")
    print()
    
    print("2️⃣  CLASSICAL COMPUTING is used for:")
    print("   ✓ Actual encryption (AES-256-GCM)")
    print("   ✓ Decryption")
    print("   ✓ File operations")
    print("   ✓ Everything except key generation")
    print()
    
    print("3️⃣  WHY this hybrid approach?")
    print(f"   • Speed: Classical encryption is {encrypt_time*1000:.3f}ms")
    print("            Quantum would be MUCH slower")
    print("   • Cost: Classical encryption is FREE")
    print("           Quantum costs $30-38 per operation")
    print("   • Practicality: You don't need quantum computer for daily use")
    print("   • Security: Quantum key + Classical encryption = Best of both!")
    print()
    
    print("4️⃣  Real analogy:")
    print("   • Quantum = The locksmith (makes the key once)")
    print("   • Classical = The lock (does the actual securing)")
    print("   • You only visit the locksmith once to get the key")
    print("   • Then you use that key in normal locks forever")
    print()
    
    print("5️⃣  When to use quantum devices:")
    print("   • simulator: FREE, for learning/testing (not secure)")
    print("   • braket (IonQ): $38/key, real quantum hardware (secure)")
    print("   • braket (Rigetti): $30/key, real quantum hardware (secure)")
    print()
    
    print("="*70)
    print("  Demo complete! You now understand quantum vs classical in nCrypt")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

