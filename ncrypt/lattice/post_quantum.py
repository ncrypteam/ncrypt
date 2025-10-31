"""
Post-Quantum Cryptography using Lattice-based primitives.

This module demonstrates Module-LWE and Module-SIS based cryptography
as described in the NCRYPT whitepaper for quantum-resistant security.
"""

import numpy as np
from typing import Tuple, List
import hashlib
import logging

logger = logging.getLogger(__name__)


class ModuleLWE:
    """
    Module Learning With Errors (Module-LWE) implementation.
    
    Provides quantum-resistant public-key encryption based on the hardness
    of the Module-LWE problem, which is believed to be secure against both
    classical and quantum computers.
    
    This is a simplified educational implementation. Production systems
    should use NIST-standardized algorithms like Kyber or Dilithium.
    """
    
    def __init__(self, n: int = 256, q: int = 3329, sigma: float = 3.2):
        """
        Initialize Module-LWE parameters.
        
        Args:
            n: Dimension of the lattice (power of 2)
            q: Modulus (prime)
            sigma: Standard deviation of error distribution
        """
        self.n = n
        self.q = q
        self.sigma = sigma
        logger.info(f"Module-LWE initialized: n={n}, q={q}, sigma={sigma}")
    
    def generate_keypair(self) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Generate a public-private keypair.
        
        Returns:
            Tuple of (public_key, private_key)
            public_key: (A, b) where b = A*s + e (mod q)
            private_key: s (secret vector)
        """
        # Generate random matrix A
        A = np.random.randint(0, self.q, size=(self.n, self.n))
        
        # Generate secret key s (small coefficients)
        s = np.random.randint(-2, 3, size=self.n)
        
        # Generate error e (Gaussian noise)
        e = np.round(np.random.normal(0, self.sigma, size=self.n)).astype(int)
        
        # Compute b = A*s + e (mod q)
        b = (A @ s + e) % self.q
        
        public_key = (A, b)
        private_key = s
        
        logger.debug("Generated Module-LWE keypair")
        return public_key, private_key
    
    def encrypt(self, public_key: Tuple[np.ndarray, np.ndarray], message_bit: int) -> Tuple[np.ndarray, int]:
        """
        Encrypt a single bit using Module-LWE.
        
        Args:
            public_key: (A, b) public key
            message_bit: 0 or 1 to encrypt
        
        Returns:
            Ciphertext (u, v)
        """
        A, b = public_key
        
        # Generate random small vector r
        r = np.random.randint(-1, 2, size=self.n)
        
        # Generate small errors
        e1 = np.round(np.random.normal(0, self.sigma, size=self.n)).astype(int)
        e2 = int(np.round(np.random.normal(0, self.sigma)))
        
        # Compute ciphertext
        u = (A.T @ r + e1) % self.q
        v = (b @ r + e2 + message_bit * (self.q // 2)) % self.q
        
        logger.debug(f"Encrypted bit {message_bit}")
        return u, v
    
    def decrypt(self, private_key: np.ndarray, ciphertext: Tuple[np.ndarray, int]) -> int:
        """
        Decrypt a ciphertext to recover the message bit.
        
        Args:
            private_key: Secret key s
            ciphertext: (u, v) ciphertext
        
        Returns:
            Decrypted bit (0 or 1)
        """
        s = private_key
        u, v = ciphertext
        
        # Compute m' = v - s^T * u (mod q)
        m_prime = (v - s @ u) % self.q
        
        # Round to nearest multiple of q/2
        if m_prime < self.q // 4 or m_prime > 3 * self.q // 4:
            message_bit = 0
        else:
            message_bit = 1
        
        logger.debug(f"Decrypted to bit {message_bit}")
        return message_bit
    
    def encrypt_bytes(self, public_key: Tuple[np.ndarray, np.ndarray], data: bytes) -> List[Tuple]:
        """
        Encrypt multiple bytes.
        
        Args:
            public_key: Public key
            data: Bytes to encrypt
        
        Returns:
            List of ciphertexts
        """
        ciphertexts = []
        for byte in data:
            for i in range(8):
                bit = (byte >> i) & 1
                ct = self.encrypt(public_key, bit)
                ciphertexts.append(ct)
        
        logger.info(f"Encrypted {len(data)} bytes to {len(ciphertexts)} ciphertexts")
        return ciphertexts
    
    def decrypt_bytes(self, private_key: np.ndarray, ciphertexts: List[Tuple]) -> bytes:
        """
        Decrypt multiple ciphertexts to bytes.
        
        Args:
            private_key: Private key
            ciphertexts: List of ciphertexts
        
        Returns:
            Decrypted bytes
        """
        bits = [self.decrypt(private_key, ct) for ct in ciphertexts]
        
        # Convert bits to bytes
        data = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= (bits[i + j] << j)
            data.append(byte)
        
        logger.info(f"Decrypted {len(ciphertexts)} ciphertexts to {len(data)} bytes")
        return bytes(data)


class ModuleSIS:
    """
    Module Short Integer Solution (Module-SIS) implementation.
    
    Provides quantum-resistant hash functions and commitment schemes
    based on the hardness of finding short vectors in lattices.
    
    This is a simplified educational implementation.
    """
    
    def __init__(self, n: int = 256, m: int = 512, q: int = 3329):
        """
        Initialize Module-SIS parameters.
        
        Args:
            n: Dimension
            m: Number of samples (m > n)
            q: Modulus
        """
        self.n = n
        self.m = m
        self.q = q
        
        # Generate random matrix A for the hash function
        self.A = np.random.randint(0, q, size=(n, m))
        
        logger.info(f"Module-SIS initialized: n={n}, m={m}, q={q}")
    
    def hash(self, data: bytes) -> np.ndarray:
        """
        Compute a quantum-resistant hash using Module-SIS.
        
        Args:
            data: Input data to hash
        
        Returns:
            Hash value as lattice vector
        """
        # Convert data to short vector
        # Use classical hash to map to small coefficients
        h = hashlib.sha256(data).digest()
        
        # Map to small coefficients
        x = np.zeros(self.m, dtype=int)
        for i in range(min(self.m, len(h) * 8)):
            byte_idx = i // 8
            bit_idx = i % 8
            x[i] = ((h[byte_idx] >> bit_idx) & 1) * 2 - 1  # Map to {-1, 1}
        
        # Compute hash: h = A * x (mod q)
        hash_value = (self.A @ x) % self.q
        
        logger.debug(f"Computed Module-SIS hash of {len(data)} bytes")
        return hash_value
    
    def commit(self, value: int, randomness: bytes = None) -> Tuple[np.ndarray, bytes]:
        """
        Create a cryptographic commitment to a value.
        
        Args:
            value: Value to commit to
            randomness: Optional randomness (generated if not provided)
        
        Returns:
            Tuple of (commitment, randomness)
        """
        if randomness is None:
            randomness = np.random.bytes(32)
        
        # Create commitment data
        commit_data = value.to_bytes(8, 'big') + randomness
        
        # Compute commitment using Module-SIS hash
        commitment = self.hash(commit_data)
        
        logger.debug(f"Created commitment for value {value}")
        return commitment, randomness
    
    def verify_commitment(self, commitment: np.ndarray, value: int, randomness: bytes) -> bool:
        """
        Verify a commitment.
        
        Args:
            commitment: Commitment to verify
            value: Claimed value
            randomness: Randomness used in commitment
        
        Returns:
            True if commitment is valid
        """
        # Recompute commitment
        commit_data = value.to_bytes(8, 'big') + randomness
        expected_commitment = self.hash(commit_data)
        
        # Compare commitments
        is_valid = np.array_equal(commitment, expected_commitment)
        
        logger.debug(f"Commitment verification: {'valid' if is_valid else 'invalid'}")
        return is_valid


class LatticeCrypto:
    """
    High-level interface for lattice-based cryptography operations.
    
    Combines Module-LWE and Module-SIS for complete quantum-resistant
    cryptographic operations as described in the NCRYPT whitepaper.
    """
    
    def __init__(self):
        """Initialize lattice cryptography system."""
        self.lwe = ModuleLWE()
        self.sis = ModuleSIS()
        logger.info("Lattice cryptography system initialized")
    
    def generate_account_keypair(self) -> Tuple[dict, dict]:
        """
        Generate a quantum-resistant account keypair.
        
        Returns:
            Tuple of (public_key_dict, private_key_dict)
        """
        pk, sk = self.lwe.generate_keypair()
        
        public_key = {
            "type": "Module-LWE",
            "A": pk[0].tolist(),
            "b": pk[1].tolist()
        }
        
        private_key = {
            "type": "Module-LWE",
            "s": sk.tolist()
        }
        
        logger.info("Generated quantum-resistant account keypair")
        return public_key, private_key
    
    def encrypt_message(self, public_key: dict, message: bytes) -> dict:
        """
        Encrypt a message using quantum-resistant encryption.
        
        Args:
            public_key: Recipient's public key
            message: Message to encrypt
        
        Returns:
            Encrypted message dictionary
        """
        # Reconstruct public key
        A = np.array(public_key["A"])
        b = np.array(public_key["b"])
        pk = (A, b)
        
        # Encrypt
        ciphertexts = self.lwe.encrypt_bytes(pk, message)
        
        # Convert to serializable format
        encrypted = {
            "ciphertexts": [(u.tolist(), int(v)) for u, v in ciphertexts],
            "algorithm": "Module-LWE"
        }
        
        logger.info(f"Encrypted message of {len(message)} bytes")
        return encrypted
    
    def decrypt_message(self, private_key: dict, encrypted: dict) -> bytes:
        """
        Decrypt a message using quantum-resistant decryption.
        
        Args:
            private_key: Recipient's private key
            encrypted: Encrypted message dictionary
        
        Returns:
            Decrypted message
        """
        # Reconstruct private key
        s = np.array(private_key["s"])
        
        # Reconstruct ciphertexts
        ciphertexts = [(np.array(u), v) for u, v in encrypted["ciphertexts"]]
        
        # Decrypt
        message = self.lwe.decrypt_bytes(s, ciphertexts)
        
        logger.info(f"Decrypted message to {len(message)} bytes")
        return message
    
    def create_value_commitment(self, amount: int) -> Tuple[np.ndarray, bytes]:
        """
        Create a cryptographic commitment to a transaction amount.
        
        Used for value-hidden transactions in NCRYPT.
        
        Args:
            amount: Transaction amount to commit
        
        Returns:
            Tuple of (commitment, opening)
        """
        return self.sis.commit(amount)
    
    def verify_value_commitment(self, commitment: np.ndarray, amount: int, opening: bytes) -> bool:
        """
        Verify a value commitment.
        
        Args:
            commitment: Commitment to verify
            amount: Claimed amount
            opening: Opening value
        
        Returns:
            True if valid
        """
        return self.sis.verify_commitment(commitment, amount, opening)

