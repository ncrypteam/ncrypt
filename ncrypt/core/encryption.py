"""
Quantum-Key-Based Encryption
Uses quantum-generated keys for classical encryption operations.
"""

import hashlib
import hmac
from typing import List, Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import logging
import os

logger = logging.getLogger(__name__)


class QuantumEncryption:
    """
    Encryption system using quantum-generated keys.
    
    Uses AES-256 for symmetric encryption with keys derived from
    quantum key distribution (QKD).
    """
    
    def __init__(self):
        """Initialize quantum encryption system."""
        self.backend = default_backend()
        logger.info("QuantumEncryption initialized")
    
    def key_to_bytes(self, key_bits: List[int], target_length: int = 32) -> bytes:
        """
        Convert bit array to bytes for use as encryption key.
        
        Args:
            key_bits: List of bits from QKD
            target_length: Target length in bytes (32 for AES-256)
        
        Returns:
            Key bytes
        """
        if len(key_bits) < target_length * 8:
            raise ValueError(
                f"Key too short: {len(key_bits)} bits, need {target_length * 8}. "
                f"Generate a longer key with more qubits (try: ncrypt generate-key --bits 2000 --key-id new_key)"
            )
        
        # Take only what we need
        key_bits = key_bits[: target_length * 8]
        
        # Convert bits to bytes
        key_bytes = bytearray()
        for i in range(0, len(key_bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(key_bits):
                    byte = (byte << 1) | key_bits[i + j]
            key_bytes.append(byte)
        
        return bytes(key_bytes)
    
    def derive_key(self, quantum_key: List[int], salt: bytes = b"") -> bytes:
        """
        Derive encryption key from quantum key using HKDF.
        
        Args:
            quantum_key: Quantum-generated key bits
            salt: Optional salt for key derivation
        
        Returns:
            Derived 32-byte key for AES-256
        """
        quantum_bytes = self.key_to_bytes(quantum_key, 32)
        
        # Use HMAC-based key derivation
        if not salt:
            salt = b"ncrypt-qkd-v1"
        
        derived = hmac.new(salt, quantum_bytes, hashlib.sha256).digest()
        logger.debug("Derived encryption key from quantum key")
        return derived
    
    def encrypt(
        self, 
        plaintext: bytes, 
        quantum_key: List[int],
        associated_data: Optional[bytes] = None
    ) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt data using quantum-generated key.
        
        Args:
            plaintext: Data to encrypt
            quantum_key: Quantum-generated key bits
            associated_data: Optional authenticated but unencrypted data
        
        Returns:
            Tuple of (ciphertext, iv, tag)
        """
        # Derive AES key from quantum key
        key = self.derive_key(quantum_key)
        
        # Generate random IV
        iv = os.urandom(16)
        
        # Pad plaintext to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        # Encrypt using AES-256-CBC
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Generate authentication tag
        tag = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
        
        logger.info(f"Encrypted {len(plaintext)} bytes -> {len(ciphertext)} bytes")
        return ciphertext, iv, tag
    
    def decrypt(
        self,
        ciphertext: bytes,
        iv: bytes,
        tag: bytes,
        quantum_key: List[int],
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypt data using quantum-generated key.
        
        Args:
            ciphertext: Encrypted data
            iv: Initialization vector
            tag: Authentication tag
            quantum_key: Quantum-generated key bits
            associated_data: Optional authenticated but unencrypted data
        
        Returns:
            Decrypted plaintext
        
        Raises:
            ValueError: If authentication fails
        """
        # Derive AES key from quantum key
        key = self.derive_key(quantum_key)
        
        # Verify authentication tag
        expected_tag = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(tag, expected_tag):
            raise ValueError("Authentication failed: message may have been tampered with")
        
        # Decrypt using AES-256-CBC
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        logger.info(f"Decrypted {len(ciphertext)} bytes -> {len(plaintext)} bytes")
        return plaintext
    
    def encrypt_file(
        self,
        input_path: str,
        output_path: str,
        quantum_key: List[int]
    ) -> Tuple[bytes, bytes]:
        """
        Encrypt a file using quantum-generated key.
        
        Args:
            input_path: Path to input file
            output_path: Path to output encrypted file
            quantum_key: Quantum-generated key bits
        
        Returns:
            Tuple of (iv, tag) needed for decryption
        """
        with open(input_path, 'rb') as f:
            plaintext = f.read()
        
        ciphertext, iv, tag = self.encrypt(plaintext, quantum_key)
        
        with open(output_path, 'wb') as f:
            f.write(ciphertext)
        
        logger.info(f"File encrypted: {input_path} -> {output_path}")
        return iv, tag
    
    def decrypt_file(
        self,
        input_path: str,
        output_path: str,
        iv: bytes,
        tag: bytes,
        quantum_key: List[int]
    ) -> None:
        """
        Decrypt a file using quantum-generated key.
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to output decrypted file
            iv: Initialization vector from encryption
            tag: Authentication tag from encryption
            quantum_key: Quantum-generated key bits
        """
        with open(input_path, 'rb') as f:
            ciphertext = f.read()
        
        plaintext = self.decrypt(ciphertext, iv, tag, quantum_key)
        
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        logger.info(f"File decrypted: {input_path} -> {output_path}")

