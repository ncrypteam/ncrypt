"""
Basic tests for nCrypt SDK.
Run with: python -m pytest tests/
"""

import pytest
import numpy as np
from ncrypt.core.qkd import BB84Protocol
from ncrypt.core.encryption import QuantumEncryption
from ncrypt.simulator.quantum_simulator import QuantumSimulator
from ncrypt.utils.key_manager import KeyManager
import tempfile
import shutil


class TestBB84Protocol:
    """Test BB84 quantum key distribution protocol."""
    
    def test_protocol_initialization(self):
        """Test BB84Protocol initialization."""
        protocol = BB84Protocol(error_threshold=0.11)
        assert protocol.error_threshold == 0.11
    
    def test_random_bit_generation(self):
        """Test random bit generation."""
        protocol = BB84Protocol()
        bits = protocol.generate_random_bits(100)
        assert len(bits) == 100
        assert all(b in [0, 1] for b in bits)
    
    def test_qubit_preparation(self):
        """Test qubit preparation."""
        protocol = BB84Protocol()
        bits = np.array([0, 1, 0, 1])
        bases = np.array([0, 0, 1, 1])
        qubits = protocol.prepare_qubits(bits, bases)
        assert len(qubits) == 4
    
    def test_key_sifting(self):
        """Test key sifting process."""
        protocol = BB84Protocol()
        alice_bits = np.array([0, 1, 1, 0, 1, 0])
        alice_bases = np.array([0, 0, 1, 1, 0, 1])
        bob_bits = np.array([0, 1, 0, 0, 1, 1])
        bob_bases = np.array([0, 0, 1, 0, 0, 1])
        
        alice_sifted, bob_sifted = protocol.sift_keys(
            alice_bits, alice_bases, bob_bits, bob_bases
        )
        
        # Bases match at indices 0, 1, 2, 4, 5 (5 matches)
        assert len(alice_sifted) == 5
        assert len(bob_sifted) == 5
    
    def test_full_protocol_low_noise(self):
        """Test full BB84 protocol with low noise."""
        protocol = BB84Protocol()
        result = protocol.run_protocol(n_bits=1000, noise_level=0.01)
        
        assert result is not None
        assert result.key_length > 0
        assert result.error_rate < 0.11
        assert len(result.final_key) == result.key_length
    
    def test_full_protocol_high_noise(self):
        """Test BB84 protocol with high noise (should fail)."""
        protocol = BB84Protocol(error_threshold=0.11)
        result = protocol.run_protocol(n_bits=1000, noise_level=0.30)
        
        # Should fail due to high error rate
        assert result is None


class TestQuantumEncryption:
    """Test quantum-key-based encryption."""
    
    def test_key_to_bytes(self):
        """Test bit array to bytes conversion."""
        qe = QuantumEncryption()
        key_bits = [1, 0, 1, 0, 1, 0, 1, 0] * 32  # 256 bits
        key_bytes = qe.key_to_bytes(key_bits, 32)
        assert len(key_bytes) == 32
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption."""
        # Generate a quantum key (need 2000+ bits to get 256 bits after BB84 processing)
        protocol = BB84Protocol()
        result = protocol.run_protocol(n_bits=2000, noise_level=0.01)
        assert result is not None
        
        # Encrypt
        qe = QuantumEncryption()
        plaintext = b"Secret quantum message!"
        ciphertext, iv, tag = qe.encrypt(plaintext, result.final_key)
        
        assert len(ciphertext) > 0
        assert len(iv) == 16
        assert len(tag) == 32
        
        # Decrypt
        decrypted = qe.decrypt(ciphertext, iv, tag, result.final_key)
        assert decrypted == plaintext
    
    def test_decrypt_wrong_key(self):
        """Test decryption with wrong key (should fail)."""
        protocol = BB84Protocol()
        result1 = protocol.run_protocol(n_bits=2000, noise_level=0.01)
        result2 = protocol.run_protocol(n_bits=2000, noise_level=0.01)
        
        qe = QuantumEncryption()
        plaintext = b"Secret message"
        ciphertext, iv, tag = qe.encrypt(plaintext, result1.final_key)
        
        # Try to decrypt with different key
        with pytest.raises(ValueError):
            qe.decrypt(ciphertext, iv, tag, result2.final_key)
    
    def test_file_encryption(self):
        """Test file encryption and decryption."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate key (need 2000+ bits to get 256 bits after BB84 processing)
            protocol = BB84Protocol()
            result = protocol.run_protocol(n_bits=2000, noise_level=0.01)
            assert result is not None
            
            # Create test file
            input_file = f"{tmpdir}/test.txt"
            encrypted_file = f"{tmpdir}/test.enc"
            decrypted_file = f"{tmpdir}/test_dec.txt"
            
            with open(input_file, 'w') as f:
                f.write("This is a test file for quantum encryption!")
            
            # Encrypt file
            qe = QuantumEncryption()
            iv, tag = qe.encrypt_file(input_file, encrypted_file, result.final_key)
            
            # Decrypt file
            qe.decrypt_file(encrypted_file, decrypted_file, iv, tag, result.final_key)
            
            # Verify
            with open(input_file, 'r') as f1, open(decrypted_file, 'r') as f2:
                assert f1.read() == f2.read()


class TestQuantumSimulator:
    """Test quantum simulator."""
    
    def test_simulator_initialization(self):
        """Test simulator initialization."""
        sim = QuantumSimulator()
        assert sim.noise_model is None
        
        sim_noisy = QuantumSimulator(noise_model='depolarizing')
        assert sim_noisy.noise_model == 'depolarizing'
    
    def test_qubit_state_creation(self):
        """Test qubit state creation."""
        sim = QuantumSimulator()
        
        # Rectilinear basis
        state_0 = sim.create_qubit_state(0, 0)
        assert np.allclose(state_0, [1, 0])
        
        state_1 = sim.create_qubit_state(1, 0)
        assert np.allclose(state_1, [0, 1])
        
        # Diagonal basis
        state_plus = sim.create_qubit_state(0, 1)
        assert np.allclose(state_plus, [1/np.sqrt(2), 1/np.sqrt(2)])
        
        state_minus = sim.create_qubit_state(1, 1)
        assert np.allclose(state_minus, [1/np.sqrt(2), -1/np.sqrt(2)])
    
    def test_measurement(self):
        """Test qubit measurement."""
        sim = QuantumSimulator()
        
        # Measure |0⟩ in rectilinear basis (should always get 0)
        state = sim.create_qubit_state(0, 0)
        results = [sim.measure_qubit(state, 0, 0) for _ in range(100)]
        assert all(r == 0 for r in results)
        
        # Measure |1⟩ in rectilinear basis (should always get 1)
        state = sim.create_qubit_state(1, 0)
        results = [sim.measure_qubit(state, 0, 0) for _ in range(100)]
        assert all(r == 1 for r in results)
    
    def test_channel_quality(self):
        """Test channel quality estimation."""
        sim = QuantumSimulator()
        stats = sim.estimate_channel_quality(n_test_qubits=1000, noise_level=0.01)
        
        assert 'error_rate' in stats
        assert 'fidelity' in stats
        assert stats['error_rate'] < 0.05  # Should be low with 1% noise
        assert stats['fidelity'] > 0.95


class TestKeyManager:
    """Test key management."""
    
    def test_save_and_load_key(self):
        """Test saving and loading keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            km = KeyManager(storage_dir=tmpdir)
            
            key = [1, 0, 1, 1, 0, 0, 1, 0] * 10
            key_id = "test_key_001"
            
            # Save key
            filepath = km.save_key(key, key_id, metadata={"protocol": "BB84"})
            assert filepath.endswith(".json")
            
            # Load key
            key_data = km.load_key(key_id)
            assert key_data["key"] == key
            assert key_data["metadata"]["key_id"] == key_id
            assert key_data["metadata"]["protocol"] == "BB84"
    
    def test_list_keys(self):
        """Test listing keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            km = KeyManager(storage_dir=tmpdir)
            
            # Save multiple keys
            for i in range(3):
                key = [1, 0] * 50
                km.save_key(key, f"key_{i:03d}")
            
            # List keys
            keys = km.list_keys()
            assert len(keys) == 3
    
    def test_delete_key(self):
        """Test deleting keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            km = KeyManager(storage_dir=tmpdir)
            
            key = [1, 0, 1, 0] * 20
            key_id = "temp_key"
            
            # Save and delete
            km.save_key(key, key_id)
            assert km.delete_key(key_id) == True
            
            # Try to load deleted key
            with pytest.raises(FileNotFoundError):
                km.load_key(key_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

