# nCrypt: Quantum-Resistant Blockchain SDK

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-beta-yellow)
![Quantum](https://img.shields.io/badge/quantum-resistant-purple)

A comprehensive SDK demonstrating the NCRYPT whitepaper concepts: quantum-resistant blockchain platform with multi-tier privacy (Transparent, Private, Accountable modes) using lattice-based post-quantum cryptography and quantum key distribution.

## 🌟 Features

### Quantum-Resistant Cryptography
- **Module-LWE Encryption**: NIST-recommended post-quantum public-key encryption
- **Module-SIS Commitments**: Quantum-resistant hash functions and commitments
- **BB84 Protocol**: Quantum key distribution for secure channels
- **Future-Proof**: Secure against both classical and quantum computers

### Multi-Tier Privacy Framework
- **Transparent Mode**: Fully visible transactions for compliance
- **Private Mode**: Maximum anonymity with hidden addresses and amounts
- **Accountable Mode**: Privacy with selective disclosure to auditors
- **DAPOA Framework**: Decentralized Anonymous Payment with Optional Accountability

### Advanced Features
- **AWS Braket Integration**: Run on real quantum devices (IonQ, Rigetti, etc.)
- **Quantum Simulator**: Test without quantum hardware
- **Key Management**: Secure storage of quantum and classical keys
- **CLI Tool**: Easy-to-use command-line interface
- **Comprehensive Logging**: Track all cryptographic operations

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ncrypteam/ncrypt
cd ncrypt

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

For [AWS Braket](https://aws.amazon.com/braket/) support:
```bash
pip install -r requirements.txt
pip install amazon-braket-sdk
```

### Basic Usage

#### 1. Initialize Configuration

```bash
ncrypt init-config
```

This creates a `config.yaml` file with default settings.

#### 2. Generate a Quantum Key

```bash
# Using Ncrypt simulator (default) - 2000 qubits ensures 256+ bit keys for encryption
ncrypt generate-key --bits 2000 --key-id my_first_key

# Using AWS Braket local simulator
ncrypt generate-key --bits 2000 --key-id braket_key --backend braket

# Note: BB84 protocol reduces key length through sifting, error checking, and privacy amplification
# 2000 qubits → ~350 final bits (sufficient for AES-256 which needs 256 bits)
```

#### 3. Encrypt a File

```bash
ncrypt encrypt --key-id my_first_key --input secret.txt --output secret.enc
```

#### 4. Decrypt a File

```bash
ncrypt decrypt --key-id my_first_key --input secret.enc --output decrypted.txt
```

#### 5. List Your Keys

```bash
ncrypt list-keys
```

## 📖 Documentation

### Python API

```python
from ncrypt.core.qkd import BB84Protocol
from ncrypt.core.encryption import QuantumEncryption
from ncrypt.utils.key_manager import KeyManager

# Generate quantum key
protocol = BB84Protocol()
result = protocol.run_protocol(n_bits=1000, noise_level=0.01)

if result:
    print(f"Key length: {result.key_length} bits")
    print(f"Error rate: {result.error_rate:.4f}")
    
    # Save the key
    km = KeyManager()
    km.save_key(result.final_key, "my_key")
    
    # Encrypt data
    qe = QuantumEncryption()
    ciphertext, iv, tag = qe.encrypt(b"Secret message", result.final_key)
    
    # Decrypt data
    plaintext = qe.decrypt(ciphertext, iv, tag, result.final_key)
    print(plaintext.decode())
```

### AWS Braket Integration

```python
from ncrypt.braket.quantum_backend import BraketBackend, BraketQKD

# Use local simulator
backend = BraketBackend(use_local_simulator=True)

# Or use real quantum device
# backend = BraketBackend(
#     device_arn="arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1"
# )

# Run BB84 protocol
qkd = BraketQKD(backend)
result = qkd.run_bb84(n_bits=500)

if result:
    print(f"Key generated on {result['device']}")
    print(f"Key length: {result['key_length']} bits")
```

## 🔬 How It Works

### BB84 Protocol

The BB84 protocol is the first quantum key distribution protocol, proposed by Charles Bennett and Gilles Brassard in 1984. It uses the principles of quantum mechanics to create a shared secret key between two parties (Alice and Bob).

**Key Steps:**

1. **Quantum Transmission**: Alice sends qubits to Bob encoded in random bases
2. **Measurement**: Bob measures qubits in randomly chosen bases
3. **Basis Reconciliation**: Alice and Bob publicly compare their bases
4. **Sifting**: Keep only bits where bases matched
5. **Error Estimation**: Check for eavesdropping by comparing a sample
6. **Privacy Amplification**: Compress the key to remove potential eavesdropper information

### Security

The security of BB84 relies on the fundamental laws of quantum mechanics:

- **No-cloning theorem**: Quantum states cannot be copied
- **Measurement disturbance**: Measuring a quantum state changes it
- **Eavesdropping detection**: Any interception attempt introduces detectable errors

If the quantum bit error rate (QBER) exceeds the threshold (typically 11%), the protocol aborts, indicating possible eavesdropping.

## 🛠️ CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `generate-key` | Generate a quantum key using BB84 protocol |
| `show-key` | Display information about a stored key |
| `list-keys` | List all stored quantum keys |
| `encrypt` | Encrypt a file using a quantum key |
| `decrypt` | Decrypt a file using a quantum key |
| `test-channel` | Test quantum channel quality |
| `init-config` | Create a default configuration file |
| `plan-execution` | **Plan operation with EXACT resource calculation** |
| `estimate-cost` | Quick cost estimate for quantum devices |
| `check-aws-costs` | Check real AWS Braket costs from billing data |

### Options

```bash
# Generate key with custom parameters
ncrypt generate-key \
  --bits 2000 \
  --noise 0.05 \
  --key-id my_key \
  --backend simulator

# Encrypt with specific key
ncrypt encrypt \
  --key-id my_key \
  --input plaintext.txt \
  --output encrypted.bin

# Test channel quality
ncrypt test-channel --bits 1000 --noise 0.01

# Estimate costs before running on real devices
ncrypt estimate-cost --bits 500 --device ionq
ncrypt estimate-cost --bits 500 --device rigetti
ncrypt estimate-cost --bits 500 --device simulator

# Check real AWS Braket costs (requires AWS CLI configured)
ncrypt check-aws-costs                    # Current month
ncrypt check-aws-costs --month 2024-10   # Specific month
ncrypt check-aws-costs --profile myprofile  # Different AWS profile
```

## 💰 AWS Cost Management

### Before Using Real Quantum Devices

#### 1. **Plan Execution (RECOMMENDED)** - Get EXACT numbers

Uses simulator to calculate exact resource usage:

```bash
# Plan with simulator (shows exact expected key length)
ncrypt plan-execution --bits 2000 --runs 5

# Output:
📊 Simulated Results (5 runs):
   Average sifted key: 1001 bits
   Average final key: 350 bits
   Final key range: 347-357 bits
   Average error rate: 0.0104
✅ Expected key (350 bits) is sufficient for encryption

# Plan with real device ARN (shows exact cost)
ncrypt plan-execution --bits 500 \
  --device-arn arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1 \
  --runs 3

# Output:
💰 AWS Braket Resources (Real Device):
   Device: Aria-1
   Circuits to execute: 500
   Shots per circuit: 1
   Total tasks: 500
   Task costs: $0.3 × 500 = $150.00
   Shot costs: $0.01 × 500 = $5.00
   TOTAL COST: $155.00
```

**Why use `plan-execution`?**
- ✅ Runs actual simulations (not estimates)
- ✅ Shows EXACT circuit counts
- ✅ Predicts exact key length range
- ✅ Calculates precise costs
- ✅ Multiple runs for statistical accuracy

#### 2. **Quick Estimate** - Fast cost calculation

```bash
# Quick cost estimate (no simulation)
ncrypt estimate-cost --bits 500 --device ionq    # ~$155
ncrypt estimate-cost --bits 500 --device rigetti # ~$150  
ncrypt estimate-cost --bits 500 --device simulator # FREE
```

### Monitor Real AWS Costs

**Check your actual AWS Braket spending:**
```bash
# Current month costs
ncrypt check-aws-costs

# Specific month
ncrypt check-aws-costs --month 2024-10

# Different AWS profile
ncrypt check-aws-costs --profile production
```

**Example output:**
```
💰 Checking AWS Braket costs...

📅 Period: 2024-10-01 to 2024-10-31
✅ AWS Account: 123456789012
   User/Role: quantum-dev

🔬 Amazon Braket
   Cost: $127.50

💵 Total Braket Cost: $127.50
💵 Total AWS Cost (all services): $458.23

⚠️  Moderate costs - monitor usage
```

### Complete Cost Protection Workflow

```bash
# 1. Plan execution (get EXACT numbers)
ncrypt plan-execution --bits 2000 \
  --device-arn arn:aws:braket:us-east-1::device/qpu/rigetti/Aspen-M-3 \
  --runs 5

# Output shows:
# - Exact circuits: 2000
# - Expected key: 350 bits (range: 347-357)
# - Exact cost: $300.35

# 2. Check current AWS spending
ncrypt check-aws-costs
# Current month: $45.23

# 3. Calculate total: $45.23 + $300.35 = $345.58

# 4. If under budget, use --dry-run to verify
ncrypt generate-key --bits 2000 --key-id prod_key \
  --backend braket \
  --device-arn arn:aws:braket:us-east-1::device/qpu/rigetti/Aspen-M-3 \
  --dry-run

# 5. Execute for real (removes --dry-run)
ncrypt generate-key --bits 2000 --key-id prod_key \
  --backend braket \
  --device-arn arn:aws:braket:us-east-1::device/qpu/rigetti/Aspen-M-3

# 6. Verify costs after
ncrypt check-aws-costs
```

### Cost Protection Best Practices

1. **Use `plan-execution`** for exact resource calculation
2. **Use `--dry-run`** flag before real execution
3. **Always check with `check-aws-costs`** before and after
4. **Set AWS Budget alerts** ($50-100/month)
5. **Start small** (100-500 circuits)
6. **Prefer Rigetti** over IonQ (28x cheaper per shot)
7. **Test on simulator** for development (always FREE)

```

## 📊 Examples

See the `examples/` directory for complete examples:

- `basic_usage.py`: End-to-end example with key generation, encryption, and decryption
- `braket_example.py`: AWS Braket integration example

Run examples:
```bash
python examples/basic_usage.py
python examples/braket_example.py
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
key_storage: ./keys

bb84:
  default_bits: 1000
  noise_level: 0.01
  error_threshold: 0.11

braket:
  use_local_simulator: true
  device_arn: null
  aws_profile: default
```

## 📈 Performance

Typical performance on a modern laptop:

- **Key Generation**: 1000 qubits in ~50ms (simulator)
- **Encryption**: 1MB file in ~10ms
- **Decryption**: 1MB file in ~10ms

AWS Braket performance depends on the quantum device and queue times.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
## 📞 Support

For issues and questions:
- GitHub Issues: [Report a bug](https://github.com/ncrypteam/ncrypt/issues)
- Documentation: See `technical_details.md` for in-depth information

## 🔮 Roadmap

- [ ] E91 protocol implementation
- [ ] Support for more quantum backends (Qiskit, Cirq)
- [ ] Post-quantum cryptographic algorithms
- [ ] Key exchange protocol over network
- [ ] GUI interface
- [ ] Docker container

---