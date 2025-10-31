# Quantum Computing Usage in nCrypt

## Overview

nCrypt employs a hybrid quantum-classical approach where quantum computing is utilized exclusively for cryptographic key generation, while classical encryption algorithms handle data encryption operations.

```
┌─────────────────────────────────────────────────────────────┐
│  KEY GENERATION (Quantum)     │  ENCRYPTION (Classical)     │
│  Uses quantum computers       │  No quantum hardware needed │
│  BB84 Protocol                │  AES-256-GCM                │
│  AWS Braket devices           │  Runs on standard hardware  │
│  Qubits & superposition       │  Proven cryptographic       │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 1: Quantum Key Generation

### Quantum Computing Components

**Command:**
```bash
$ ncrypt generate-key --bits 2000 --key-id my_key --device braket
```

**Process:**

1. **Quantum State Preparation** (AWS Braket / Quantum Hardware)
   ```
   Alice prepares qubits in random bases:
   - Rectilinear basis: |0⟩ or |1⟩
   - Diagonal basis:   |+⟩ or |-⟩
   
   Example: Bit=1, Basis=Diagonal → Creates qubit in |−⟩ state
   ```

2. **Quantum Channel Transmission** (Simulated)
   ```
   Qubits transmitted through quantum channel with noise modeling
   - Superposition maintained during transmission
   - Quantum mechanics ensures eavesdropping detection
   ```

3. **Quantum Measurement** (Bob measures qubits)
   ```
   Bob randomly chooses measurement bases
   - Same basis as Alice → Deterministic result
   - Different basis → Random outcome (50/50 probability)
   ```

4. **BB84 Protocol** (Quantum Key Distribution)
   ```
   Protocol steps:
   - Alice & Bob compare bases publicly
   - Keep bits where bases matched
   - Discard approximately 50% where bases differed
   - Verify security through error rate analysis
   - Perform privacy amplification
   
   Result: Shared secret key with quantum security guarantees
   ```

**Security Properties:**
- Quantum mechanics properties enable eavesdropping detection
- No-cloning theorem prevents copying of unknown quantum states
- Heisenberg uncertainty ensures measurement disturbs quantum states
- Eavesdropper cannot intercept without introducing detectable errors

**Cost:** $30-$38 per key generation on real quantum hardware

---

## Part 2: Classical Encryption/Decryption

### Classical Computing Components

**Commands:**
```bash
$ ncrypt encrypt secret.txt --key-id my_key --output secret.enc
$ ncrypt decrypt secret.enc --key-id my_key --output decrypted.txt
```

**Implementation:**

```python
# Classical AES-256-GCM encryption
def encrypt(plaintext, quantum_key):
    # 1. Derive AES key from quantum key bits
    aes_key = derive_key(quantum_key)  # SHA-256 hashing
    
    # 2. Encrypt using standard AES-256-GCM
    cipher = AES.new(aes_key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    
    return ciphertext, cipher.nonce, tag
```

**Rationale for Classical Encryption:**
1. **Performance**: Classical encryption operates at millions of bytes/second
2. **Efficiency**: Quantum operations are resource-intensive and costly
3. **Practicality**: No quantum hardware required for daily operations
4. **Standard Practice**: Industry-standard approach in post-quantum cryptography

**Cost:** Free (executes on local hardware)

---

## Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ONE-TIME: Generate quantum key (resource-intensive)            │
│         ↓                                                       │
│    [Quantum Key Stored Locally]                                │
│         ↓                                                       │
│  REPEATED: Encrypt files (efficient, classical)                │
│         ↓                                                       │
│    [Encrypted Files]                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Operational Example

```bash
# Step 1: Generate quantum key (ONE TIME)
$ ncrypt generate-key --bits 2000 --key-id company_master_key --device braket
Quantum operations on AWS Braket...
Cost: $38.00 (one-time)
Key generated (256 bits final)

# Step 2: Encrypt multiple files (UNLIMITED USAGE)
$ ncrypt encrypt payroll.xlsx --key-id company_master_key
Encrypted in 0.003 seconds (free)

$ ncrypt encrypt database.sql --key-id company_master_key  
Encrypted in 0.120 seconds (free)

$ ncrypt encrypt secrets.json --key-id company_master_key
Encrypted in 0.001 seconds (free)
```

**Single quantum key enables unlimited classical encryption operations**

---

## Design Rationale

### Limitations of Pure Quantum Encryption

- **Speed**: Quantum gates operate at millisecond timescales
- **Cost**: $0.08 per shot × millions of operations
- **Scalability**: Cannot efficiently encrypt large datasets
- **Unnecessary**: Classical encryption is secure with proper key management

### Advantages of Hybrid Approach

- **Quantum Key Generation**: Exploits quantum properties for provable security
- **Classical Encryption**: Fast, proven, practical implementation
- **Optimal Trade-off**: Quantum security guarantees with classical efficiency

---

## Technical Implementation Details

### Quantum Key Generation (BB84):

```
1. Alice prepares qubits: |0⟩, |1⟩, |+⟩, |-⟩
2. Bob measures in random bases
3. Basis comparison (discard ~50%)
4. Error rate verification for eavesdropping detection
5. Privacy amplification via universal hashing
→ Result: Quantum-secure key bits
```

### Classical Encryption (AES-256-GCM):

```
1. Load quantum key from storage
2. Derive AES key: SHA-256(quantum_key)
3. Encrypt: AES-GCM(plaintext, aes_key)
4. Output: ciphertext + IV + authentication tag
→ Result: Encrypted data with authenticated encryption
```

---

## Device Comparison

### Simulator (Local, Free)
- Mathematical simulation of quantum behavior
- Instant execution
- Not quantum-secure (pseudorandom)
- Use case: Development and testing

### AWS Braket - IonQ Forte ($38/key)
- Real quantum hardware (trapped ion technology)
- 36 qubits with #AQ 36 (Algorithmic Qubits)
- True quantum randomness via quantum measurement
- 0.4% 2-qubit gate error rate
- All-to-all qubit connectivity
- T1/T2 coherence: 10-100s / ~1s
- Official Documentation: https://ionq.com/quantum-systems/forte
- Use case: Production deployments, maximum fidelity

### AWS Braket - Rigetti Ankaa-3 ($30/key)
- Real quantum hardware (superconducting qubit technology)
- 82-qubit processor with tunable couplers
- Square lattice architecture with high connectivity
- True quantum randomness via quantum measurement
- Cost-effective option for production workloads
- Official Documentation: https://qcs.rigetti.com/qpus
- Use case: Production deployments, budget-conscious implementations

---

## Security Analysis

### Classical Cryptography Limitations:
- Security based on computational complexity assumptions
- RSA: Vulnerable to Shor's algorithm on quantum computers
- Potential future vulnerabilities to quantum attacks

### Quantum Cryptography Advantages:
- Security based on fundamental physics
- No-cloning theorem: Mathematically proven
- Measurement disturbance: Fundamental to quantum mechanics
- Resistant to quantum computing attacks (physics-based security)

---

## Command Reference

```bash
# Generate key (Quantum)
ncrypt generate-key --bits 2000 --key-id mykey --device simulator
ncrypt generate-key --bits 2000 --key-id mykey --device braket --backend ionq
ncrypt generate-key --bits 2000 --key-id mykey --device braket --backend rigetti

# Encrypt file (Classical)
ncrypt encrypt secret.txt --key-id mykey --output secret.enc

# Decrypt file (Classical)  
ncrypt decrypt secret.enc --key-id mykey --output decrypted.txt

# Check pricing
ncrypt show-pricing

# Estimate costs
ncrypt estimate-cost --bits 2000 --device ionq
```

---

## Summary

**Quantum Computing Usage:**
- Exclusive to cryptographic key generation
- Leverages quantum mechanical properties for provable security
- One-time cost per key

**Classical Computing Usage:**
- All encryption and decryption operations
- Standard cryptographic algorithms (AES-256-GCM)
- Unlimited usage at no additional cost

**Hybrid Approach Benefits:**
- Combines quantum security guarantees with classical efficiency
- Industry-standard practice for post-quantum cryptography
- Practical implementation for production systems

---

## References

### Scientific Literature
- Bennett & Brassard (1984): BB84 Protocol
- Quantum Key Distribution: Theoretical foundations
- AES-256: NIST-approved encryption standard
- Hybrid Cryptography: Post-quantum cryptographic practices

### Quantum Hardware Documentation
- IonQ Forte System: https://ionq.com/quantum-systems/forte
- Rigetti QCS Platform: https://qcs.rigetti.com/qpus
- AWS Braket Documentation: https://docs.aws.amazon.com/braket/
