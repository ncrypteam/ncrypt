# Understanding BB84 Key Length

## Why Does My Key Get Shorter?

The BB84 quantum key distribution protocol involves several steps that reduce the final key length. This is **normal and necessary** for security!

## Key Length Reduction Process

### Starting Point: Raw Qubits
```
Example: 2000 qubits exchanged
```

### Step 1: Basis Sifting (~50% kept)
Alice and Bob only keep bits where they used the **same measurement basis**.

```
2000 qubits → ~1000 bits (50% matching bases)
```

### Step 2: Error Checking (50% used)
To detect eavesdropping, they publicly compare about **half** the sifted bits to calculate the Quantum Bit Error Rate (QBER).

```
1000 bits → ~500 bits remaining (after checking)
```

### Step 3: Privacy Amplification (70% retained)
To reduce any information an eavesdropper might have, they compress the key using hash functions.

```
500 bits → ~350 bits final key (70% compression factor)
```

## Final Result

```
2000 raw qubits → ~350 final key bits
```

This is **sufficient for AES-256 encryption** which needs 256 bits!

## Recommended Qubit Counts

| Use Case | Qubits Needed | Expected Final Key |
|----------|---------------|-------------------|
| AES-128 | 1000 | ~175 bits |
| AES-256 | **2000** | ~350 bits ✅ |
| Extra margin | 3000 | ~525 bits |
| High security | 5000 | ~875 bits |

## Why This Reduction Is Important

### 1. Security (Basis Sifting)
- Only bits measured in matching bases are correlated
- Prevents information leakage from wrong-basis measurements

### 2. Eavesdropping Detection (Error Checking)
- Comparing a sample detects quantum interception
- QBER > 11% → abort (eavesdropper present!)
- This is the **core security feature** of QKD

### 3. Information Reduction (Privacy Amplification)
- Reduces any partial information Eve might have
- Uses universal hash functions
- Ensures Eve has negligible information about final key

## Practical Examples

### ❌ Too Few Qubits
```bash
ncrypt generate-key --bits 1000 --key-id short_key
# Result: ~175 bits (too short for AES-256!)
```

### ✅ Correct Amount
```bash
ncrypt generate-key --bits 2000 --key-id good_key
# Result: ~350 bits (perfect for AES-256!)
```

### ✅ Extra Safety Margin
```bash
ncrypt generate-key --bits 3000 --key-id long_key
# Result: ~525 bits (extra security margin)
```

## Understanding the Warning

If you see:
```
⚠️ Note: Key is 175 bits (< 256 bits)
   This key is too short for AES-256 encryption
   Generate a new key with more qubits (try --bits 2000)
```

**Solution**: Generate a new key with more qubits:
```bash
ncrypt generate-key --bits 2000 --key-id new_key
```

## Quick Reference

### Default Behavior
```bash
# CLI now defaults to 2000 qubits
ncrypt generate-key --key-id my_key
# Automatically uses 2000 qubits → ~350 bit key
```

### Custom Amount
```bash
# Specify exactly how many qubits you want
ncrypt generate-key --bits 5000 --key-id big_key
```

## Mathematical Formula

For a rough estimate of final key length:

```
Final_Key_Length ≈ Raw_Qubits × 0.5 × 0.5 × 0.7
                 ≈ Raw_Qubits × 0.175

Example: 2000 × 0.175 = 350 bits
```

**Factors:**
- 0.5 = basis sifting (50% match)
- 0.5 = error checking (50% kept)
- 0.7 = privacy amplification (70% retained)

## Real-World Variation

The actual final key length varies based on:
- **Random basis matching**: Sometimes you get lucky!
- **Channel noise**: Higher noise → more bits discarded
- **Error threshold**: More stringent checking → fewer bits

**Typical range for 2000 qubits**: 300-400 bits

## Configuration

You can adjust parameters in `config.yaml`:

```yaml
bb84:
  default_bits: 2000            # Starting qubits
  check_sample_ratio: 0.5       # How much to use for error checking
  error_threshold: 0.11         # Maximum acceptable QBER
```

## Why Can't We Just Use More Bits?

On **simulators**: We can! Use as many as you want.

On **real quantum devices**:
- Quantum operations are expensive (time and cost)
- More qubits = longer execution time
- Trade-off between key length and practicality

**Best practice**: Use 2000-3000 qubits for good balance.

## Summary

✅ **2000 qubits is the recommended default**
- Produces ~350 bit keys
- Perfect for AES-256 (needs 256 bits)
- Good balance of security and efficiency

✅ **Key reduction is a feature, not a bug**
- Ensures security against eavesdropping
- Provides information-theoretic security
- This is what makes QKD special!

✅ **Always check your key length**
- CLI now warns if key is too short
- Error message provides helpful guidance
- Generate longer keys if needed

---

**TL;DR**: Use `--bits 2000` or more for encryption! 🔐

