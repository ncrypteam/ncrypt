# nCrypt: Technical Details

This document provides in-depth technical information about the nCrypt SDK implementation, quantum protocols, and cryptographic operations.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [BB84 Protocol Implementation](#bb84-protocol-implementation)
3. [Quantum Simulator](#quantum-simulator)
4. [AWS Braket Integration](#aws-braket-integration)
5. [Encryption System](#encryption-system)
6. [Security Analysis](#security-analysis)
7. [Performance Considerations](#performance-considerations)
8. [API Reference](#api-reference)

## Architecture Overview

### System Components

```
ncrypt/
├── core/                 # Core quantum cryptography implementations
│   ├── qkd.py           # BB84 protocol
│   └── encryption.py    # Quantum-key-based encryption
├── simulator/           # Quantum simulators
│   └── quantum_simulator.py
├── braket/             # AWS Braket integration
│   └── quantum_backend.py
├── utils/              # Utilities
│   └── key_manager.py  # Key storage and management
└── cli/                # Command-line interface
    └── main.py
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    BB84 Protocol Flow                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Alice                    Quantum Channel              Bob  │
│    │                                                    │    │
│    ├──► Generate random bits                           │    │
│    ├──► Generate random bases                          │    │
│    ├──► Prepare qubits ──────────────────────────────► │    │
│    │                                                    ├──► │
│    │                                              Measure    │
│    │                                           (random bases)│
│    │◄────────── Classical Channel ────────────────────►│    │
│    │         (Compare bases publicly)                  │    │
│    │                                                    │    │
│    ├──► Sift key (matching bases)                      │    │
│    │                                                    ├──► │
│    │◄────── Sample comparison for error checking ─────►│    │
│    │                                                    │    │
│    ├──► Privacy amplification                          │    │
│    │                                                    ├──► │
│    ▼                                                    ▼    │
│  Final Key                                         Final Key │
└─────────────────────────────────────────────────────────────┘
```

## BB84 Protocol Implementation

### Quantum States

The BB84 protocol uses four quantum states in two conjugate bases:

**Rectilinear Basis (Computational Basis)**:
- |0⟩ = [1, 0]ᵀ  (represents bit 0)
- |1⟩ = [0, 1]ᵀ  (represents bit 1)

**Diagonal Basis (Hadamard Basis)**:
- |+⟩ = (|0⟩ + |1⟩)/√2 = [1/√2, 1/√2]ᵀ  (represents bit 0)
- |-⟩ = (|0⟩ - |1⟩)/√2 = [1/√2, -1/√2]ᵀ  (represents bit 1)

### Protocol Steps

#### 1. Quantum Transmission Phase

```python
def prepare_qubits(bits, bases):
    """
    Prepare qubits based on bits and bases.
    
    Encoding:
    - bit=0, basis=0 → |0⟩
    - bit=1, basis=0 → |1⟩
    - bit=0, basis=1 → |+⟩
    - bit=1, basis=1 → |-⟩
    """
    qubits = []
    for bit, basis in zip(bits, bases):
        if basis == 0:  # Rectilinear
            state = [1, 0] if bit == 0 else [0, 1]
        else:  # Diagonal
            state = [1/√2, 1/√2] if bit == 0 else [1/√2, -1/√2]
        qubits.append((state, basis))
    return qubits
```

#### 2. Measurement Phase

When Bob measures a qubit:
- **Same basis as Alice**: Measurement is deterministic (Bob gets Alice's bit)
- **Different basis**: Measurement is random (50% chance of each outcome)

**Measurement Operators**:

Rectilinear basis:
- M₀ = |0⟩⟨0| = [[1, 0], [0, 0]]
- M₁ = |1⟩⟨1| = [[0, 0], [0, 1]]

Diagonal basis:
- M₀ = |+⟩⟨+| = [[0.5, 0.5], [0.5, 0.5]]
- M₁ = |-⟩⟨-| = [[0.5, -0.5], [-0.5, 0.5]]

#### 3. Key Sifting

After basis reconciliation, approximately 50% of bits are kept (those with matching bases).

Expected sifted key length: `n_raw / 2`

#### 4. Error Estimation

Sample `k` bits from sifted key to estimate Quantum Bit Error Rate (QBER):

```
QBER = (number of mismatches) / k
```

**Security threshold**: If QBER > 11%, abort protocol (possible eavesdropping).

#### 5. Privacy Amplification

Reduce Eve's (eavesdropper's) information using universal hash functions. In our implementation:

```python
def privacy_amplification(key, compression_factor=0.7):
    """
    Compress key to reduce potential information leakage.
    
    New length = original_length × compression_factor
    """
    new_length = int(len(key) * compression_factor)
    # Apply hash function (simplified: XOR of segments)
    amplified_key = []
    step = len(key) // new_length
    for i in range(new_length):
        segment = key[i*step : (i+1)*step]
        amplified_key.append(XOR(segment))
    return amplified_key
```

### Error Sources

1. **Quantum Channel Noise**: Natural decoherence and loss
2. **Detector Inefficiency**: Imperfect single-photon detectors
3. **Eavesdropping**: Active interception by Eve

## Quantum Simulator

### State Vector Simulation

The simulator implements full state vector simulation for 1-qubit systems:

```python
class QuantumSimulator:
    def create_qubit_state(self, bit, basis):
        """Create quantum state vector."""
        if basis == 0:  # Rectilinear
            return np.array([1, 0]) if bit == 0 else np.array([0, 1])
        else:  # Diagonal
            return np.array([1, 1])/np.sqrt(2) if bit == 0 \
                   else np.array([1, -1])/np.sqrt(2)
    
    def measure_qubit(self, state, basis):
        """
        Measure qubit in given basis.
        
        Probability of outcome i:
        P(i) = |⟨i|ψ⟩|² = |Mᵢ|ψ⟩|²
        """
        M0, M1 = self.get_measurement_operator(basis)
        prob_0 = np.abs(np.vdot(state, M0 @ state))
        prob_1 = np.abs(np.vdot(state, M1 @ state))
        
        # Normalize and sample
        total = prob_0 + prob_1
        return np.random.choice([0, 1], p=[prob_0/total, prob_1/total])
```

### Noise Models

#### Depolarizing Noise

Models random Pauli errors (X, Y, Z):

```python
def apply_depolarizing_noise(state, p):
    """
    Apply depolarizing noise with probability p.
    
    ρ → (1-p)ρ + p·I/2
    """
    mixed_state = np.array([0.5, 0.5])
    return (1 - p) * state + p * mixed_state
```

#### Amplitude Damping

Models energy loss (T₁ relaxation):

```python
def apply_amplitude_damping(state, γ):
    """
    Apply amplitude damping with rate γ.
    
    |0⟩ → |0⟩
    |1⟩ → √(1-γ)|1⟩ + √γ|0⟩
    """
    new_state = state.copy()
    new_state[0] += np.sqrt(γ) * state[1]
    new_state[1] *= np.sqrt(1 - γ)
    return new_state / np.linalg.norm(new_state)
```

## AWS Braket Integration

### Circuit Construction

BB84 circuit for a single qubit:

```python
def create_bb84_circuit(bit, encode_basis, measure_basis):
    """
    Create Braket circuit for BB84.
    
    Encoding:
    - bit=1, basis=0: Apply X gate
    - bit=0, basis=1: Apply H gate
    - bit=1, basis=1: Apply H, then Z gate
    
    Measurement:
    - basis=1: Apply H gate before measurement
    """
    circuit = Circuit()
    
    # Encode bit
    if encode_basis == 0:
        if bit == 1:
            circuit.x(0)
    else:
        circuit.h(0)
        if bit == 1:
            circuit.z(0)
    
    # Measure
    if measure_basis == 1:
        circuit.h(0)
    circuit.measure(0)
    
    return circuit
```

### Supported Devices

| Device | Provider | Qubits | Gate Set | Typical QBER |
|--------|----------|--------|----------|--------------|
| IonQ Aria-1 | IonQ | 25 | Universal | ~0.001 |
| Rigetti Aspen-M-3 | Rigetti | 80 | Parametric | ~0.01 |
| Local Simulator | Amazon | Unlimited | Universal | Configurable |

### Cost Optimization

**Batch Processing**: Group circuits to minimize task overhead.

```python
def run_batch_qkd(bits, batch_size=100):
    """
    Run QKD in batches to optimize costs.
    
    Cost per task: ~$0.30
    Cost per shot: ~$0.01 (IonQ) or ~$0.00035 (Rigetti)
    """
    results = []
    for i in range(0, len(bits), batch_size):
        batch = bits[i:i+batch_size]
        tasks = [device.run(circuit, shots=1) for circuit in batch]
        results.extend([task.result() for task in tasks])
    return results
```

## Encryption System

### Key Derivation

Convert quantum key bits to encryption key:

```python
def derive_key(quantum_key_bits, salt=b"ncrypt-qkd-v1"):
    """
    Derive AES-256 key from quantum key using HMAC-SHA256.
    
    quantum_key_bits → bytes → HMAC-SHA256 → AES-256 key
    """
    # Convert bits to bytes
    quantum_bytes = bits_to_bytes(quantum_key_bits[:256])
    
    # Derive key using HMAC
    key = hmac.new(salt, quantum_bytes, hashlib.sha256).digest()
    return key  # 32 bytes for AES-256
```

### Encryption Scheme

**Algorithm**: AES-256-CBC with HMAC-SHA256 authentication

```python
def encrypt(plaintext, quantum_key):
    """
    Encrypt data using quantum-derived key.
    
    1. Derive AES key from quantum key
    2. Generate random IV
    3. Pad plaintext (PKCS7)
    4. Encrypt with AES-256-CBC
    5. Compute HMAC tag for authentication
    """
    key = derive_key(quantum_key)
    iv = os.urandom(16)
    
    # Pad and encrypt
    padded = pkcs7_pad(plaintext, 128)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(padded)
    
    # Authenticate
    tag = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
    
    return ciphertext, iv, tag
```

### Security Properties

1. **Confidentiality**: AES-256 (256-bit key space: 2²⁵⁶ combinations)
2. **Authentication**: HMAC-SHA256 (prevents tampering)
3. **Key Uniqueness**: Each QKD session generates unique key
4. **Forward Secrecy**: Compromised key doesn't affect past/future keys

## Security Analysis

### Threat Model

#### Intercept-Resend Attack

**Attack**: Eve intercepts qubits, measures them, and resends.

**Detection**: Eve must guess Bob's basis (50% error rate). This exceeds the 11% threshold, triggering abort.

**Example**:
- Alice sends 1000 qubits
- Eve intercepts all, measures in random bases
- Expected errors: ~250 (25% QBER)
- Protocol aborts ✓

#### Photon Number Splitting (PNS)

**Attack**: Eve splits multi-photon pulses and stores copies.

**Mitigation**: Use true single-photon sources or decoy states (future implementation).

#### Man-in-the-Middle

**Attack**: Eve impersonates both Alice and Bob.

**Mitigation**: Authenticated classical channel (not yet implemented - requires pre-shared secret or public key infrastructure).

### Information-Theoretic Security

BB84 provides **unconditional security** based on:

1. **No-cloning theorem**: Eve cannot copy unknown quantum states
2. **Uncertainty principle**: Measuring in wrong basis destroys information
3. **Quantum disturbance**: Any measurement changes the state

**Security proof**: Proven secure against any attack limited by quantum mechanics (Shor-Preskill 2000).

## Performance Considerations

### Key Generation Rate

**Simulator**:
- Raw qubit rate: ~20,000 qubits/second
- Final key rate: ~7,000 bits/second (after sifting and amplification)

**AWS Braket (IonQ)**:
- Circuit execution: ~1-2 seconds per shot
- Batch of 100 circuits: ~120 seconds
- Effective rate: ~0.8 qubits/second

**Bottleneck**: Quantum device queue time and circuit execution.

### Scalability

| Operation | Complexity | Note |
|-----------|------------|------|
| Qubit preparation | O(n) | Linear in number of qubits |
| Measurement | O(n) | Linear in number of qubits |
| Basis reconciliation | O(n) | Linear comparison |
| Error estimation | O(k) | k = sample size |
| Privacy amplification | O(m) | m = final key length |

**Total**: O(n) where n is number of raw qubits.

### Memory Usage

- **Simulator**: ~16 bytes per qubit (complex128)
- **Key storage**: ~1 byte per 8 bits + metadata
- **Encryption**: Minimal overhead (streaming possible)

## API Reference

### Core Classes

#### BB84Protocol

```python
class BB84Protocol:
    def __init__(self, error_threshold: float = 0.11)
    def run_protocol(self, n_bits: int, noise_level: float, 
                     check_sample_ratio: float) -> Optional[QKDResult]
```

**Parameters**:
- `error_threshold`: Maximum acceptable QBER (default: 0.11)
- `n_bits`: Number of qubits to exchange
- `noise_level`: Simulated channel noise (0.0 - 0.5)
- `check_sample_ratio`: Fraction of sifted key for error checking

**Returns**: `QKDResult` object containing:
- `final_key`: List of key bits
- `key_length`: Length of final key
- `error_rate`: Measured QBER
- `discarded_bits`: Number of discarded bits

#### QuantumEncryption

```python
class QuantumEncryption:
    def encrypt(self, plaintext: bytes, quantum_key: List[int]) 
        -> Tuple[bytes, bytes, bytes]
    def decrypt(self, ciphertext: bytes, iv: bytes, tag: bytes,
                quantum_key: List[int]) -> bytes
```

**Encryption returns**: (ciphertext, iv, tag)
**Decryption raises**: `ValueError` if authentication fails

#### KeyManager

```python
class KeyManager:
    def __init__(self, storage_dir: str = "./keys")
    def save_key(self, key: List[int], key_id: str, 
                 metadata: Optional[Dict] = None) -> str
    def load_key(self, key_id: str) -> Dict
    def list_keys(self) -> List[Dict]
    def delete_key(self, key_id: str) -> bool
```

### Simulator Classes

#### QuantumSimulator

```python
class QuantumSimulator:
    def __init__(self, noise_model: Optional[str] = None)
    def simulate_qkd_exchange(self, alice_bits, alice_bases,
                              bob_bases, noise_level) -> List[int]
    def estimate_channel_quality(self, n_test_qubits: int,
                                  noise_level: float) -> dict
```

### Braket Classes

#### BraketBackend

```python
class BraketBackend:
    def __init__(self, device_arn: Optional[str], 
                 use_local_simulator: bool = True)
    def run_qkd_exchange(self, alice_bits, alice_bases, bob_bases,
                         shots: int = 1) -> List[int]
    def get_device_info(self) -> Dict
    def estimate_cost(self, n_circuits: int) -> Dict
```

## References

1. Bennett, C. H., & Brassard, G. (1984). "Quantum cryptography: Public key distribution and coin tossing." *Proceedings of IEEE International Conference on Computers, Systems and Signal Processing*, 175-179.

2. Shor, P. W., & Preskill, J. (2000). "Simple proof of security of the BB84 quantum key distribution protocol." *Physical Review Letters*, 85(2), 441.

3. Scarani, V., et al. (2009). "The security of practical quantum key distribution." *Reviews of Modern Physics*, 81(3), 1301.

4. Lo, H. K., Curty, M., & Tamaki, K. (2014). "Secure quantum key distribution." *Nature Photonics*, 8(8), 595-604.

5. Amazon Web Services (2024). "Amazon Braket Documentation." https://aws.amazon.com/braket/

## Appendix A: Quantum Gates

| Gate | Matrix | Effect |
|------|--------|--------|
| X (NOT) | [[0,1],[1,0]] | Bit flip: \|0⟩↔\|1⟩ |
| Z | [[1,0],[0,-1]] | Phase flip: \|1⟩→-\|1⟩ |
| H (Hadamard) | [[1,1],[1,-1]]/√2 | Basis change |
| I (Identity) | [[1,0],[0,1]] | No change |

## Appendix B: Glossary

- **QBER**: Quantum Bit Error Rate - percentage of errors in sifted key
- **Qubit**: Quantum bit - fundamental unit of quantum information
- **Sifting**: Process of discarding bits measured in mismatched bases
- **Privacy Amplification**: Compression to reduce eavesdropper information
- **Fidelity**: Measure of quantum state similarity (1 = perfect)
- **Decoherence**: Loss of quantum properties due to environment

---

*Last updated: October 2024*

