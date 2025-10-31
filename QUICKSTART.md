# nCrypt Quick Start Guide

Get up and running with nCrypt in 5 minutes!

## Installation

```bash
cd /Users/borker/coin_projects/ncrypt

# Install the package and dependencies
pip install -e .

# Verify installation
ncrypt --help
```

## Quick Demo

### 1. Initialize Configuration

```bash
ncrypt init-config
```

This creates a `config.yaml` file with sensible defaults.

### 2. Generate Your First Quantum Key

```bash
ncrypt generate-key --bits 2000 --key-id my_first_key
```

Output:
```
Generating quantum key with 2000 qubits...
Backend: simulator
✅ Key generated successfully!
   Key ID: my_first_key
   Length: 350 bits
   Error rate: 0.0080

✅ Key is sufficient for AES-256 encryption (350 >= 256 bits)
```

**Note**: BB84 protocol reduces the final key length through:
- Basis sifting (~50% kept)
- Error checking (50% used)
- Privacy amplification (70% retained)

That's why 2000 qubits → ~350 final bits (perfect for encryption!)

### 3. View Your Key

```bash
ncrypt show-key --key-id my_first_key
```

### 4. Encrypt a File

Create a test file:
```bash
echo "This is a secret message!" > secret.txt
```

Encrypt it:
```bash
ncrypt encrypt --key-id my_first_key --input secret.txt --output secret.enc
```

### 5. Decrypt the File

```bash
ncrypt decrypt --key-id my_first_key --input secret.enc --output decrypted.txt

# Verify
cat decrypted.txt
```

### 6. List All Keys

```bash
ncrypt list-keys
```

## Python API Example

Save this as `test_ncrypt.py`:

```python
#!/usr/bin/env python3
"""Quick test of nCrypt SDK."""

from ncrypt.core.qkd import BB84Protocol
from ncrypt.core.encryption import QuantumEncryption

# Generate quantum key
print("Generating quantum key...")
protocol = BB84Protocol()
result = protocol.run_protocol(n_bits=1000, noise_level=0.01)

if result:
    print(f"✅ Key generated: {result.key_length} bits")
    print(f"   Error rate: {result.error_rate:.4f}")
    
    # Encrypt a message
    plaintext = b"Hello from the quantum realm!"
    qe = QuantumEncryption()
    ciphertext, iv, tag = qe.encrypt(plaintext, result.final_key)
    print(f"✅ Message encrypted: {len(ciphertext)} bytes")
    
    # Decrypt
    decrypted = qe.decrypt(ciphertext, iv, tag, result.final_key)
    print(f"✅ Message decrypted: {decrypted.decode()}")
else:
    print("❌ Key generation failed!")
```

Run it:
```bash
python test_ncrypt.py
```

## Using AWS Braket (Optional)

### Setup AWS Credentials

```bash
# Install AWS CLI and Braket SDK
pip install awscli amazon-braket-sdk

# Configure AWS credentials
aws configure
```

### Generate Key on Braket Local Simulator

```bash
ncrypt generate-key \
  --bits 500 \
  --key-id braket_key \
  --backend braket
```

### Generate Key on Real Quantum Device

```bash
# Estimate cost first
ncrypt generate-key \
  --bits 100 \
  --key-id ionq_key \
  --backend braket \
  --device-arn arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1
```

**Note**: Real quantum devices incur costs (~$0.30/task + per-shot fees).

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=ncrypt --cov-report=html
```

## Examples

Run the included examples:

```bash
# Basic usage example
python examples/basic_usage.py

# AWS Braket example
python examples/braket_example.py
```

## Common Operations

### Test Channel Quality

```bash
ncrypt test-channel --bits 1000 --noise 0.01
```

### Generate High-Security Key

```bash
ncrypt generate-key \
  --bits 5000 \
  --noise 0.005 \
  --key-id high_security_key
```

### Encrypt Large File

```bash
ncrypt generate-key --bits 2000 --key-id file_key
ncrypt encrypt --key-id file_key --input largefile.pdf --output largefile.enc
```

## Directory Structure

After setup, your project should look like:

```
ncrypt/
├── config.yaml          # Configuration file
├── keys/                # Quantum keys storage
├── examples/            # Example scripts
├── ncrypt/              # SDK source code
├── tests/               # Test suite
├── README.md            # Full documentation
├── technical_details.md # Technical reference
└── QUICKSTART.md        # This file
```

## Configuration

Edit `config.yaml` to customize:

```yaml
key_storage: ./keys      # Where to store quantum keys
bb84:
  default_bits: 1000     # Default key size
  noise_level: 0.01      # Simulated noise
  error_threshold: 0.11  # Security threshold
```

## Next Steps

- Read `README.md` for comprehensive documentation
- Read `technical_details.md` for deep technical insights
- Explore `examples/` directory for more use cases
- Check out the BB84 protocol implementation in `ncrypt/core/qkd.py`

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the ncrypt directory
cd /Users/borker/coin_projects/ncrypt

# Reinstall in development mode
pip install -e .
```

### AWS Braket Errors

```bash
# Install Braket SDK
pip install amazon-braket-sdk

# Check AWS credentials
aws sts get-caller-identity
```

### Key Generation Fails

- Check if noise level is too high (>0.15)
- Increase number of bits (try 2000+)
- Check logs for detailed error messages

## Getting Help

- GitHub Issues: Report bugs and request features
- Documentation: See `README.md` and `technical_details.md`
- Examples: Check `examples/` directory

## What's Next?

Now that you have nCrypt working:

1. ✅ Try encrypting different types of files
2. ✅ Experiment with different noise levels
3. ✅ Test with AWS Braket local simulator
4. ✅ Explore the Python API for custom applications
5. ✅ Read the technical documentation to understand BB84 protocol

**Happy quantum cryptography!** 🔐⚛️

