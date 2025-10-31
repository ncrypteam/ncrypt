# Quick Reference: Quantum vs Classical in nCrypt

## 🎯 One-Page Cheat Sheet for Fresh Grads

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    WHEN IS IT QUANTUM?                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    ╔════════════════════════════╗        ╔═══════════════════════════╗
    ║   QUANTUM COMPUTING ⚛️      ║        ║   CLASSICAL COMPUTING 💻   ║
    ║   (Key Generation)         ║        ║   (Encryption/Decryption) ║
    ╠════════════════════════════╣        ╠═══════════════════════════╣
    ║                            ║        ║                           ║
    ║ ncrypt generate-key        ║        ║ ncrypt encrypt            ║
    ║                            ║        ║ ncrypt decrypt            ║
    ║ Uses:                      ║        ║                           ║
    ║ • Superposition states     ║        ║ Uses:                     ║
    ║ • Quantum measurement      ║        ║ • AES-256-GCM             ║
    ║ • BB84 protocol            ║        ║ • SHA-256 hashing         ║
    ║                            ║        ║ • Regular CPU operations  ║
    ║ Runs on:                   ║        ║                           ║
    ║ • AWS Braket               ║        ║ Runs on:                  ║
    ║ • IonQ/Rigetti devices     ║        ║ • Your laptop             ║
    ║ • Quantum simulator        ║        ║ • Any computer            ║
    ║                            ║        ║ • No quantum needed       ║
    ║ Cost:                      ║        ║                           ║
    ║ • Simulator: FREE          ║        ║ Cost:                     ║
    ║ • Real device: $30-38      ║        ║ • Always FREE             ║
    ║                            ║        ║                           ║
    ║ Speed:                     ║        ║ Speed:                    ║
    ║ • ~0.028s for key gen      ║        ║ • 0.006s for encryption   ║
    ║                            ║        ║ • 0.0001s for decryption  ║
    ║                            ║        ║                           ║
    ║ Frequency:                 ║        ║ Frequency:                ║
    ║ • Once per key             ║        ║ • As many times as needed ║
    ║                            ║        ║                           ║
    ╚════════════════════════════╝        ╚═══════════════════════════╝
            │                                        ▲
            │ Produces                               │
            │                                        │ Uses
            └────────> [Quantum Key] ─────────────────┘
                       Stored locally


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    TYPICAL WORKFLOW                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Step 1: Generate key with quantum computer (ONCE)
───────────────────────────────────────────────────────────────
$ ncrypt generate-key --bits 2000 --key-id mykey --device braket
⚛️  Quantum operations happening on AWS Braket...
💰 Cost: $38 (one-time)
✅ Key saved locally

Step 2: Encrypt files with classical computer (MANY TIMES)
───────────────────────────────────────────────────────────────
$ ncrypt encrypt file1.txt --key-id mykey
💻 Classical AES encryption...
✅ Done in 0.003s (FREE)

$ ncrypt encrypt file2.txt --key-id mykey
💻 Classical AES encryption...
✅ Done in 0.005s (FREE)

$ ncrypt encrypt file3.txt --key-id mykey
💻 Classical AES encryption...
✅ Done in 0.002s (FREE)

... use the same quantum key forever!


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    COMMON QUESTIONS                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Q: Is my file being encrypted by a quantum computer?
A: NO! Your file is encrypted with classical AES-256.
   Only the KEY was generated using quantum.

Q: Do I need a quantum computer to decrypt files?
A: NO! Decryption uses regular CPU, just like encryption.

Q: What makes it "quantum cryptography" then?
A: The key was generated using quantum mechanics (BB84 protocol).
   This makes it theoretically unbreakable (physics, not math).

Q: Can I use `encrypt` without internet?
A: YES! Encryption is local and classical. No quantum access needed.

Q: Can I use `generate-key` without internet?
A: Only with --device simulator (free but not secure).
   Real quantum devices need AWS Braket connection.

Q: Why not encrypt directly with quantum?
A: Too slow! Quantum gates are ~1000x slower than classical.
   Classical encryption with quantum keys is the best approach.


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    DEVICE COMPARISON                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

simulator (Local, FREE)
─────────────────────────────────────────────────────────────
✓ No quantum hardware (just math simulation)
✓ Instant and free
✗ Not quantum-secure (uses pseudorandom)
✗ Don't use for production
Use for: Learning, testing, demos

braket --backend ionq (IonQ Forte, $38/key)
─────────────────────────────────────────────────────────────
✓ Real quantum computer (trapped ions)
✓ True quantum randomness
✓ Quantum-secure key generation
✓ Higher fidelity
Cost: $0.30/task + $0.08/shot = ~$38 per key
Use for: Production, maximum security

braket --backend rigetti (Rigetti Ankaa-3, $30/key)
─────────────────────────────────────────────────────────────
✓ Real quantum computer (superconducting qubits)
✓ True quantum randomness
✓ Quantum-secure key generation
✓ Cheaper than IonQ
Cost: $0.30/task + $0.0009/shot = ~$30 per key
Use for: Production, budget-conscious


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    REAL ANALOGY                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Think of it like your house:

🔑 QUANTUM (Key Generation)
   You go to a special quantum locksmith once
   They use quantum mechanics to create an unbreakable key
   Costs $30-38
   You do this ONCE

🏠 CLASSICAL (Encryption/Decryption)
   You use that key in regular locks on your doors
   Open/close your doors as many times as you want
   Free and instant
   You do this DAILY

The quantum part makes the key.
The classical part uses the key.

You don't need a quantum locksmith to open your door every day!
You just use the key they gave you.


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    TECHNICAL DETAILS                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Quantum Key Generation (BB84):
  1. Alice prepares qubits: |0⟩, |1⟩, |+⟩, |-⟩
  2. Bob measures in random bases
  3. They compare bases (discard ~50%)
  4. Check for eavesdropping (error rate)
  5. Privacy amplification
  → Result: Quantum-secure key bits

Classical Encryption (AES-256-GCM):
  1. Load quantum key from disk
  2. Derive AES key: SHA-256(quantum_key)
  3. Encrypt: AES-GCM(plaintext, aes_key)
  4. Output: ciphertext + IV + tag
  → Result: Encrypted data


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    COMMAND QUICK REF                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# Generate key (QUANTUM)
ncrypt generate-key --bits 2000 --key-id mykey --device simulator
ncrypt generate-key --bits 2000 --key-id mykey --device braket --backend ionq
ncrypt generate-key --bits 2000 --key-id mykey --device braket --backend rigetti

# Encrypt file (CLASSICAL)
ncrypt encrypt secret.txt --key-id mykey --output secret.enc

# Decrypt file (CLASSICAL)  
ncrypt decrypt secret.enc --key-id mykey --output decrypted.txt

# Check pricing (API call)
ncrypt show-pricing

# Estimate costs (Calculator)
ncrypt estimate-cost --bits 2000 --device ionq


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    REMEMBER                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✅ Quantum = KEY generation (once, expensive, special hardware)
✅ Classical = ENCRYPTION (unlimited, free, any computer)
✅ Best of both worlds = Secure + Practical

Don't overthink it! 
- Making the key = Quantum 🌀
- Using the key = Classical 💻

