# Quick Reference: Quantum vs Classical Computing in nCrypt

## System Architecture Overview

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    COMPONENT BREAKDOWN                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    ╔════════════════════════════╗        ╔═══════════════════════════╗
    ║   QUANTUM COMPUTING        ║        ║   CLASSICAL COMPUTING     ║
    ║   (Key Generation)         ║        ║   (Encryption/Decryption) ║
    ╠════════════════════════════╣        ╠═══════════════════════════╣
    ║                            ║        ║                           ║
    ║ ncrypt generate-key        ║        ║ ncrypt encrypt            ║
    ║                            ║        ║ ncrypt decrypt            ║
    ║ Components:                ║        ║                           ║
    ║ • Superposition states     ║        ║ Components:               ║
    ║ • Quantum measurement      ║        ║ • AES-256-GCM             ║
    ║ • BB84 protocol            ║        ║ • SHA-256 hashing         ║
    ║                            ║        ║ • Standard CPU operations ║
    ║ Infrastructure:            ║        ║                           ║
    ║ • AWS Braket               ║        ║ Infrastructure:           ║
    ║ • IonQ/Rigetti devices     ║        ║ • Local hardware          ║
    ║ • Quantum simulator        ║        ║ • Any standard computer   ║
    ║                            ║        ║ • No quantum required     ║
    ║ Cost:                      ║        ║                           ║
    ║ • Simulator: Free          ║        ║ Cost:                     ║
    ║ • Real device: $30-38      ║        ║ • Always free             ║
    ║                            ║        ║                           ║
    ║ Performance:               ║        ║ Performance:              ║
    ║ • ~0.028s for key gen      ║        ║ • 0.006s for encryption   ║
    ║                            ║        ║ • 0.0001s for decryption  ║
    ║                            ║        ║                           ║
    ║ Frequency:                 ║        ║ Frequency:                ║
    ║ • Once per key             ║        ║ • Unlimited usage         ║
    ║                            ║        ║                           ║
    ╚════════════════════════════╝        ╚═══════════════════════════╝
            │                                        ▲
            │ Produces                               │
            │                                        │ Consumes
            └────────> [Quantum Key] ─────────────────┘
                       (Stored locally)
```

---

## Typical Workflow

### Step 1: Generate Key with Quantum Computer (One-Time Operation)

```bash
$ ncrypt generate-key --bits 2000 --key-id mykey --device braket
Quantum operations on AWS Braket
Cost: $38 (one-time expense)
Result: Key stored locally
```

### Step 2: Encrypt Files with Classical Computer (Unlimited Usage)

```bash
$ ncrypt encrypt file1.txt --key-id mykey
Classical AES encryption
Completed in 0.003s (free)

$ ncrypt encrypt file2.txt --key-id mykey
Classical AES encryption
Completed in 0.005s (free)

$ ncrypt encrypt file3.txt --key-id mykey
Classical AES encryption
Completed in 0.002s (free)
```

Single quantum key enables unlimited classical encryption operations.

---

## Technical Questions

### Q: Is file encryption performed by quantum computer?
**A:** No. Files are encrypted using classical AES-256 algorithm. Only the cryptographic key was generated using quantum processes.

### Q: Is quantum hardware required for decryption?
**A:** No. Decryption uses standard CPU operations, identical to encryption.

### Q: What constitutes "quantum cryptography"?
**A:** The cryptographic key is generated using quantum mechanical principles (BB84 protocol), providing theoretical security guarantees based on physics rather than computational complexity.

### Q: Can encryption operate without internet connectivity?
**A:** Yes. Encryption is local and classical. No quantum hardware access required for encryption/decryption operations.

### Q: Can key generation operate without internet connectivity?
**A:** Only with `--device simulator` flag (free but not quantum-secure). Real quantum devices require AWS Braket network connection.

### Q: Why not perform encryption directly with quantum computer?
**A:** Performance constraints. Quantum gates operate approximately 1000× slower than classical operations. The hybrid approach provides optimal performance while maintaining quantum security guarantees.

---

## Device Comparison

### Simulator (Local, Free)
```
Advantages:
✓ No quantum hardware (mathematical simulation)
✓ Instant execution
✓ No cost

Limitations:
✗ Not quantum-secure (pseudorandom)
✗ Unsuitable for production

Use Case: Development, testing, demonstrations
```

### AWS Braket - IonQ Forte ($38/key)
```
Specifications:
✓ Trapped ion quantum computer
✓ 36 qubits (#AQ 36)
✓ 0.4% 2-qubit gate error
✓ All-to-all connectivity
✓ T1/T2: 10-100s / ~1s
✓ True quantum randomness

Pricing: $0.30/task + $0.08/shot ≈ $38 per key

Documentation: https://ionq.com/quantum-systems/forte

Use Case: Production deployments, maximum fidelity requirements
```

### AWS Braket - Rigetti Ankaa-3 ($30/key)
```
Specifications:
✓ Superconducting quantum computer
✓ 82-qubit processor
✓ Square lattice with tunable couplers
✓ True quantum randomness
✓ Cost-effective option

Pricing: $0.30/task + $0.0009/shot ≈ $30 per key

Documentation: https://qcs.rigetti.com/qpus

Use Case: Production deployments, cost-conscious implementations
```

---

## Technical Implementation

### Quantum Key Generation (BB84):
```
1. Alice prepares qubits: |0⟩, |1⟩, |+⟩, |-⟩
2. Bob performs random basis measurements
3. Basis comparison (discard ~50% mismatched)
4. Error rate verification
5. Privacy amplification
→ Output: Quantum-secure key bits
```

### Classical Encryption (AES-256-GCM):
```
1. Load quantum key from storage
2. Derive AES key: SHA-256(quantum_key)
3. Encrypt: AES-GCM(plaintext, aes_key)
4. Output: ciphertext + IV + tag
→ Output: Authenticated encrypted data
```

---

## Command Reference

```bash
# Quantum Key Generation
ncrypt generate-key --bits 2000 --key-id mykey --device simulator
ncrypt generate-key --bits 2000 --key-id mykey --device braket --backend ionq
ncrypt generate-key --bits 2000 --key-id mykey --device braket --backend rigetti

# Classical Encryption
ncrypt encrypt secret.txt --key-id mykey --output secret.enc

# Classical Decryption
ncrypt decrypt secret.enc --key-id mykey --output decrypted.txt

# Pricing Information
ncrypt show-pricing

# Cost Estimation
ncrypt estimate-cost --bits 2000 --device ionq
```

---

## Key Concepts

### Quantum Computing Usage:
- Key generation only (one-time operation)
- Resource-intensive and costly
- Requires specialized hardware

### Classical Computing Usage:
- Encryption and decryption (unlimited operations)
- Computationally efficient
- Executes on standard hardware

### Hybrid Approach Benefits:
- Quantum security guarantees
- Classical computational efficiency
- Production-ready implementation
