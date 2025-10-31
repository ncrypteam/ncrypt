# When Does nCrypt Use Quantum Computing?


```
┌─────────────────────────────────────────────────────────────┐
│  KEY GENERATION (Quantum)     │  ENCRYPTION (Classical)     │
│  ✓ Uses quantum computers     │  ✗ No quantum needed        │
│  ✓ BB84 Protocol              │  ✓ Uses AES-256-GCM         │
│  ✓ AWS Braket devices         │  ✓ Runs on your laptop      │
│  ✓ Qubits & superposition     │  ✓ Fast & proven secure     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Part 1: KEY GENERATION (Quantum Computing)

### ⚛️ **USES QUANTUM COMPUTING**

**What happens:**
```bash
$ ncrypt generate-key --bits 2000 --key-id my_key --device braket
```

**Behind the scenes:**

1. **🌀 Quantum State Preparation** (AWS Braket / Real Quantum Hardware)
   ```
   Alice prepares qubits in random bases:
   - Rectilinear basis: |0⟩ or |1⟩
   - Diagonal basis:   |+⟩ or |-⟩
   
   Example: Bit=1, Basis=Diagonal → Creates qubit in |−⟩ state
   ```

2. **📡 Quantum Transmission** (Simulated quantum channel)
   ```
   Qubits travel through "quantum channel" with noise
   - Superposition maintained during transmission
   - Quantum mechanics ensures eavesdropping detection
   ```

3. **📊 Quantum Measurement** (Bob measures qubits)
   ```
   Bob randomly chooses measurement bases
   - Same basis as Alice → Correct bit (deterministic)
   - Different basis → Random result (50/50)
   ```

4. **🔐 BB84 Protocol** (Quantum Key Distribution)
   ```
   Alice & Bob compare bases publicly:
   - Keep bits where bases matched
   - Discard ~50% where bases differed
   - Check for eavesdropping (error rate)
   - Perform privacy amplification
   
   Result: Shared secret key that's quantum-secure!
   ```

**Why quantum here?**
- **Quantum mechanics properties** make eavesdropping detectable
- **No-cloning theorem**: You can't copy an unknown quantum state
- **Heisenberg uncertainty**: Measuring changes the state
- **Eve (eavesdropper) can't intercept without leaving traces**

**Cost:** $30-$38 per key generation (uses real quantum circuits)

---

## 🔒 Part 2: ENCRYPTION/DECRYPTION (Classical Computing)

### 💻 **NO QUANTUM NEEDED**

**What happens:**
```bash
$ ncrypt encrypt secret.txt --key-id my_key --output secret.enc
$ ncrypt decrypt secret.enc --key-id my_key --output decrypted.txt
```

**Behind the scenes:**

```python
# Classical AES-256-GCM encryption (runs on your CPU)
def encrypt(plaintext, quantum_key):
    # 1. Derive AES key from quantum key bits
    aes_key = derive_key(quantum_key)  # Classical hashing
    
    # 2. Encrypt using standard AES-256-GCM
    cipher = AES.new(aes_key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    
    return ciphertext, cipher.nonce, tag
```

**Why NOT quantum here?**
1. **Speed**: Classical encryption is FAST (millions of bytes/sec)
2. **Efficiency**: Quantum operations are slow and expensive
3. **Practicality**: No quantum computer needed for daily encryption
4. **Standard practice**: Even post-quantum crypto uses classical encryption

**Cost:** FREE (runs locally on your machine)

---

## 🎯 The Hybrid Approach: Best of Both Worlds

```
┌─────────────────────────────────────────────────────────────────┐
│                    HOW nCrypt WORKS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ONCE: Generate quantum key (expensive, quantum)                │
│         ↓                                                       │
│    [Quantum Key Stored Locally]                                │
│         ↓                                                       │
│  MANY TIMES: Encrypt files (free, classical)                   │
│         ↓                                                       │
│    [Encrypted Files]                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Real-World Example

```bash
# Step 1: Generate quantum key (QUANTUM - Uses AWS Braket)
$ ncrypt generate-key --bits 2000 --key-id company_master_key --device braket
⚛️  Using IonQ quantum device...
💰 Cost: $38.00
✓ Quantum key generated (256 bits final)

# Step 2: Encrypt many files (CLASSICAL - Free and fast)
$ ncrypt encrypt payroll.xlsx --key-id company_master_key
✓ Encrypted in 0.003 seconds (FREE)

$ ncrypt encrypt database.sql --key-id company_master_key  
✓ Encrypted in 0.120 seconds (FREE)

$ ncrypt encrypt secrets.json --key-id company_master_key
✓ Encrypted in 0.001 seconds (FREE)
```

**One quantum key → Encrypt unlimited files classically**

---

## 🤔 Why This Design?

### Problem: Pure Quantum Encryption Would Be

❌ **Too Slow**: Quantum gates take milliseconds  
❌ **Too Expensive**: $0.08 per shot × millions of operations  
❌ **Too Limited**: Can't encrypt large files  
❌ **Unnecessary**: Classical encryption is already secure IF the key is secret  

### Solution: Hybrid Quantum-Classical

✅ **Quantum for key generation**: Exploits quantum properties for security  
✅ **Classical for encryption**: Fast, proven, practical  
✅ **Best of both**: Quantum security + Classical speed  

---

## 📊 Visual Comparison

```
╔════════════════════════════════════════════════════════════╗
║                  QUANTUM vs CLASSICAL                      ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  KEY GENERATION                                           ║
║  ┌─────────────────────────────────────────────────┐     ║
║  │ Quantum Computer (AWS Braket)                   │     ║
║  │                                                 │     ║
║  │  Alice ──[|0⟩,|+⟩,|1⟩,|-⟩]──> Bob              │     ║
║  │                                                 │     ║
║  │  ⚛️  Superposition                              │     ║
║  │  ⚛️  Entanglement                               │     ║
║  │  ⚛️  Quantum measurement                        │     ║
║  │                                                 │     ║
║  │  Output: [1,0,1,1,0,0,1,...]                   │     ║
║  └─────────────────────────────────────────────────┘     ║
║                        ↓                                   ║
║            ┌──────────────────────┐                       ║
║            │   Quantum Key        │                       ║
║            │  (Stored locally)    │                       ║
║            └──────────────────────┘                       ║
║                        ↓                                   ║
║  ENCRYPTION/DECRYPTION                                    ║
║  ┌─────────────────────────────────────────────────┐     ║
║  │ Your Laptop (Classical CPU)                     │     ║
║  │                                                 │     ║
║  │  AES-256-GCM Encryption                        │     ║
║  │                                                 │     ║
║  │  💻 Boolean logic                               │     ║
║  │  💻 XOR operations                              │     ║
║  │  💻 Substitution boxes                          │     ║
║  │                                                 │     ║
║  │  "Hello" + Key → "ƒ∂˙∆∂∆£"                     │     ║
║  └─────────────────────────────────────────────────┘     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🔬 Technical Deep Dive

### Quantum Key Generation Code Path

```python
# ncrypt/core/qkd.py - BB84Protocol.run_protocol()

# QUANTUM PARTS:
alice_bits = generate_random_bits(2000)          # Classical RNG
alice_bases = generate_random_bases(2000)        # Classical RNG

# → This gets sent to quantum device:
qubits = prepare_qubits(alice_bits, alice_bases) # ⚛️ QUANTUM
#        Creates actual quantum states like:
#        |ψ⟩ = α|0⟩ + β|1⟩  (superposition)

# → Quantum transmission happens here (simulated):
bob_bases = generate_random_bases(2000)          # Classical RNG  
bob_bits = measure_qubits(qubits, bob_bases)     # ⚛️ QUANTUM
#           Quantum measurement collapses superposition

# CLASSICAL PARTS (post-quantum):
alice_sifted, bob_sifted = sift_keys(...)        # Classical comparison
error_rate = estimate_error_rate(...)            # Classical statistics
final_key = privacy_amplification(...)           # Classical hashing
```

### Classical Encryption Code Path

```python
# ncrypt/core/encryption.py - QuantumEncryption.encrypt()

# ALL CLASSICAL - No quantum computer needed:

def encrypt(plaintext, quantum_key):
    # 1. Convert quantum key bits to bytes (classical)
    key_bytes = key_to_bytes(quantum_key)
    
    # 2. Derive AES key using SHA-256 (classical)
    aes_key = SHA256(key_bytes)
    
    # 3. Standard AES-256-GCM encryption (classical)
    cipher = AES.new(aes_key, MODE_GCM)
    ciphertext = cipher.encrypt(plaintext)
    
    return ciphertext  # Pure classical cryptography
```

---

## 🎯 When to Use Each Device

```bash
# Local Simulator (FREE - No quantum, just simulation)
$ ncrypt generate-key --device simulator
Use when: Testing, development, learning
⚠️  Not quantum-secure (uses pseudorandom numbers)

# AWS Braket - IonQ ($38 per key)
$ ncrypt generate-key --device braket --backend ionq
Use when: Production, real quantum security needed
✓ Real quantum hardware
✓ True quantum randomness
✓ Eavesdropping detection

# AWS Braket - Rigetti ($30 per key, cheaper!)
$ ncrypt generate-key --device braket --backend rigetti
Use when: Budget matters, slightly lower fidelity OK
✓ Real quantum hardware
✓ Lower cost per shot
```

---

## 💡 Key Takeaways for Fresh Grads

1. **Quantum ≠ Magic encryption**
   - It's used for KEY GENERATION only
   - Actual encryption is still classical (AES)

2. **Why BB84 is quantum**
   - Uses actual quantum states (superposition)
   - Measurements collapse the state
   - Physics guarantees security, not math

3. **Why encryption stays classical**
   - Fast (GHz CPU vs MHz quantum gates)
   - Cheap (free vs $30-$38 per key)
   - Proven secure with quantum keys

4. **Hybrid approach**
   - Quantum: Generate unbreakable keys
   - Classical: Actually encrypt your data
   - Best of both worlds!

5. **Real-world analogy**
   - Quantum: The locksmith (makes the key)
   - Classical: The lock (does the actual securing)
   - You only need the locksmith once!

---

## 🔍 See It In Action

```bash
# Watch quantum operations (verbose mode)
$ ncrypt generate-key --bits 2000 --key-id demo --device braket -v

# You'll see quantum-specific operations:
⚛️  Preparing qubits in superposition...
⚛️  Sending through quantum channel...
⚛️  Bob measuring in random bases...
📊 Sifting: 2000 qubits → 1000 sifted bits (bases matched)
🔍 Error check: 2.1% error rate (quantum noise)
✓ Below threshold - channel secure!
🔐 Privacy amplification: 1000 → 700 final bits
💾 Saving quantum key locally...

# Then watch classical encryption (instant!)
$ ncrypt encrypt largefile.zip --key-id demo -v

# You'll see classical operations:
💻 Loading quantum key from disk...
💻 Deriving AES-256 key...
💻 Encrypting with AES-GCM...
✓ Encrypted 50 MB in 0.23 seconds
```

---

## 📚 Further Reading

- **BB84 Protocol**: Original paper by Bennett & Brassard (1984)
- **Quantum Key Distribution**: How quantum mechanics enables secure key exchange
- **AES-256**: Why classical encryption is still used for bulk data
- **Hybrid Cryptography**: Combining quantum and classical for practical security

---

## ❓ Common Questions

**Q: Why not encrypt directly with quantum computers?**  
A: Too slow and expensive. Classical encryption with quantum keys is optimal.

**Q: Is the encryption quantum-resistant?**  
A: Yes! The key is quantum-generated, making it secure against quantum attacks.

**Q: Can I use the simulator for production?**  
A: No - it's pseudorandom. Use real quantum devices (braket) for security.

**Q: How often should I generate new keys?**  
A: Depends on your security model. One key can encrypt many files safely.

**Q: What makes BB84 quantum?**  
A: It uses actual quantum superposition and measurement. Can't be done classically.

---

*Generated by nCrypt - Quantum Cryptography SDK*

