"""
Quantum Key Distribution (QKD) Implementation
Implements the BB84 protocol for secure key exchange using quantum mechanics.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QKDResult:
    """Result of a QKD session."""
    raw_key: List[int]
    sifted_key: List[int]
    final_key: List[int]
    error_rate: float
    key_length: int
    discarded_bits: int
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return {
            "final_key_length": self.key_length,
            "error_rate": self.error_rate,
            "discarded_bits": self.discarded_bits,
            "efficiency": self.key_length / (self.key_length + self.discarded_bits) if (self.key_length + self.discarded_bits) > 0 else 0
        }


class BB84Protocol:
    """
    BB84 Quantum Key Distribution Protocol.
    
    The BB84 protocol, proposed by Bennett and Brassard in 1984, is the first
    quantum cryptography protocol. It uses quantum mechanics to ensure secure
    communication between two parties (Alice and Bob).
    
    Protocol steps:
    1. Alice generates random bits and random bases
    2. Alice prepares qubits in chosen bases
    3. Bob measures qubits in randomly chosen bases
    4. Alice and Bob compare bases (classical channel)
    5. Sift key: keep only bits where bases matched
    6. Error estimation and privacy amplification
    """
    
    # Basis types
    RECTILINEAR = 0  # |0⟩, |1⟩ basis
    DIAGONAL = 1      # |+⟩, |-⟩ basis
    
    def __init__(self, error_threshold: float = 0.11):
        """
        Initialize BB84 protocol.
        
        Args:
            error_threshold: Maximum acceptable quantum bit error rate (QBER)
                           Default 0.11 (11%) is typical for secure communication
        """
        self.error_threshold = error_threshold
        logger.info(f"BB84Protocol initialized with error threshold: {error_threshold}")
    
    def generate_random_bits(self, n: int) -> np.ndarray:
        """Generate n random bits."""
        return np.random.randint(0, 2, n)
    
    def generate_random_bases(self, n: int) -> np.ndarray:
        """Generate n random measurement bases."""
        return np.random.randint(0, 2, n)
    
    def prepare_qubits(self, bits: np.ndarray, bases: np.ndarray) -> List[Tuple[int, int]]:
        """
        Prepare qubits based on bits and bases.
        
        Encoding:
        - Rectilinear basis (0): 0 -> |0⟩, 1 -> |1⟩
        - Diagonal basis (1):   0 -> |+⟩, 1 -> |-⟩
        
        Returns:
            List of (bit, basis) tuples representing prepared qubits
        """
        qubits = [(int(bit), int(basis)) for bit, basis in zip(bits, bases)]
        logger.debug(f"Prepared {len(qubits)} qubits")
        return qubits
    
    def measure_qubits(
        self, 
        qubits: List[Tuple[int, int]], 
        bases: np.ndarray,
        noise_level: float = 0.0
    ) -> np.ndarray:
        """
        Measure qubits in given bases.
        
        Args:
            qubits: List of (bit, basis) tuples from Alice
            bases: Measurement bases chosen by Bob
            noise_level: Simulated quantum channel noise (0.0 to 0.5)
        
        Returns:
            Measured bits
        """
        measured_bits = []
        
        for (alice_bit, alice_basis), bob_basis in zip(qubits, bases):
            if alice_basis == bob_basis:
                # Same basis: measurement is deterministic (plus noise)
                if np.random.random() < noise_level:
                    # Bit flip due to noise
                    measured_bits.append(1 - alice_bit)
                else:
                    measured_bits.append(alice_bit)
            else:
                # Different basis: measurement is random (50/50)
                measured_bits.append(np.random.randint(0, 2))
        
        logger.debug(f"Measured {len(measured_bits)} qubits with noise level {noise_level}")
        return np.array(measured_bits)
    
    def sift_keys(
        self,
        alice_bits: np.ndarray,
        alice_bases: np.ndarray,
        bob_bits: np.ndarray,
        bob_bases: np.ndarray
    ) -> Tuple[List[int], List[int]]:
        """
        Sift keys: keep only bits where Alice and Bob used the same basis.
        
        Returns:
            Tuple of (alice_sifted_key, bob_sifted_key)
        """
        matching_bases = alice_bases == bob_bases
        alice_sifted = alice_bits[matching_bases].tolist()
        bob_sifted = bob_bits[matching_bases].tolist()
        
        logger.info(f"Sifted key length: {len(alice_sifted)} (from {len(alice_bits)} raw bits)")
        return alice_sifted, bob_sifted
    
    def estimate_error_rate(
        self,
        alice_key: List[int],
        bob_key: List[int],
        sample_size: Optional[int] = None
    ) -> Tuple[float, List[int], List[int]]:
        """
        Estimate quantum bit error rate (QBER).
        
        Alice and Bob publicly compare a random sample of their bits.
        These bits are discarded after comparison.
        
        Args:
            alice_key: Alice's sifted key
            bob_key: Bob's sifted key
            sample_size: Number of bits to sample (default: 50% of key)
        
        Returns:
            Tuple of (error_rate, remaining_alice_key, remaining_bob_key)
        """
        key_length = len(alice_key)
        if sample_size is None:
            sample_size = key_length // 2
        
        if sample_size >= key_length:
            raise ValueError("Sample size must be smaller than key length")
        
        # Randomly select indices to check
        check_indices = np.random.choice(key_length, sample_size, replace=False)
        keep_indices = np.array([i for i in range(key_length) if i not in check_indices])
        
        # Calculate error rate
        errors = sum(1 for i in check_indices if alice_key[i] != bob_key[i])
        error_rate = errors / sample_size
        
        # Keep remaining bits
        remaining_alice = [alice_key[i] for i in keep_indices]
        remaining_bob = [bob_key[i] for i in keep_indices]
        
        logger.info(f"QBER: {error_rate:.4f} ({errors}/{sample_size} errors)")
        return error_rate, remaining_alice, remaining_bob
    
    def privacy_amplification(self, key: List[int], compression_factor: float = 0.7) -> List[int]:
        """
        Privacy amplification: compress key to reduce Eve's information.
        
        In a real implementation, this would use universal hash functions.
        Here we use a simplified version for demonstration.
        
        Args:
            key: Input key
            compression_factor: How much to compress (0.0 to 1.0)
        
        Returns:
            Compressed key
        """
        new_length = int(len(key) * compression_factor)
        if new_length == 0:
            return []
        
        # Simplified privacy amplification using XOR of adjacent bits
        amplified = []
        step = len(key) // new_length
        
        for i in range(new_length):
            start_idx = i * step
            end_idx = min(start_idx + step, len(key))
            # XOR all bits in this segment
            segment_bit = 0
            for j in range(start_idx, end_idx):
                segment_bit ^= key[j]
            amplified.append(segment_bit)
        
        logger.info(f"Privacy amplification: {len(key)} -> {len(amplified)} bits")
        return amplified
    
    def run_protocol(
        self,
        n_bits: int = 1000,
        noise_level: float = 0.01,
        check_sample_ratio: float = 0.5
    ) -> Optional[QKDResult]:
        """
        Run complete BB84 protocol.
        
        Args:
            n_bits: Number of qubits to exchange
            noise_level: Channel noise level (0.0 to 0.5)
            check_sample_ratio: Fraction of sifted key to use for error checking
        
        Returns:
            QKDResult if successful, None if error rate too high
        """
        logger.info(f"Starting BB84 protocol with {n_bits} qubits, noise={noise_level}")
        
        # Step 1: Alice generates random bits and bases
        alice_bits = self.generate_random_bits(n_bits)
        alice_bases = self.generate_random_bases(n_bits)
        
        # Step 2: Alice prepares qubits
        qubits = self.prepare_qubits(alice_bits, alice_bases)
        
        # Step 3: Bob generates random bases and measures
        bob_bases = self.generate_random_bases(n_bits)
        bob_bits = self.measure_qubits(qubits, bob_bases, noise_level)
        
        # Step 4: Sift keys (Alice and Bob compare bases)
        alice_sifted, bob_sifted = self.sift_keys(
            alice_bits, alice_bases, bob_bits, bob_bases
        )
        
        if len(alice_sifted) == 0:
            logger.error("No matching bases found")
            return None
        
        # Step 5: Error estimation
        sample_size = int(len(alice_sifted) * check_sample_ratio)
        error_rate, alice_final, bob_final = self.estimate_error_rate(
            alice_sifted, bob_sifted, sample_size
        )
        
        # Step 6: Check if error rate is acceptable
        if error_rate > self.error_threshold:
            logger.warning(
                f"Error rate {error_rate:.4f} exceeds threshold {self.error_threshold}. "
                "Possible eavesdropping detected!"
            )
            return None
        
        # Step 7: Privacy amplification
        final_key = self.privacy_amplification(alice_final)
        
        result = QKDResult(
            raw_key=alice_bits.tolist(),
            sifted_key=alice_sifted,
            final_key=final_key,
            error_rate=error_rate,
            key_length=len(final_key),
            discarded_bits=n_bits - len(final_key)
        )
        
        logger.info(f"BB84 protocol completed successfully. Final key length: {len(final_key)}")
        return result

