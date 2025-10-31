"""
Quantum Simulator
Simulates quantum operations for testing and development without hardware.
"""

import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class QuantumSimulator:
    """
    Simulates quantum operations for QKD protocols.
    
    This simulator implements basic quantum operations needed for
    quantum key distribution, including qubit preparation, measurement,
    and channel simulation.
    """
    
    def __init__(self, noise_model: Optional[str] = None):
        """
        Initialize quantum simulator.
        
        Args:
            noise_model: Type of noise to simulate ('depolarizing', 'amplitude_damping', None)
        """
        self.noise_model = noise_model
        self.shots = 1024
        logger.info(f"QuantumSimulator initialized with noise model: {noise_model}")
    
    def create_qubit_state(self, bit: int, basis: int) -> np.ndarray:
        """
        Create a qubit state vector.
        
        Args:
            bit: 0 or 1
            basis: 0 (rectilinear) or 1 (diagonal)
        
        Returns:
            2D state vector
        """
        if basis == 0:  # Rectilinear basis
            if bit == 0:
                # |0⟩ state
                return np.array([1.0, 0.0], dtype=complex)
            else:
                # |1⟩ state
                return np.array([0.0, 1.0], dtype=complex)
        else:  # Diagonal basis
            if bit == 0:
                # |+⟩ state = (|0⟩ + |1⟩) / √2
                return np.array([1.0, 1.0], dtype=complex) / np.sqrt(2)
            else:
                # |-⟩ state = (|0⟩ - |1⟩) / √2
                return np.array([1.0, -1.0], dtype=complex) / np.sqrt(2)
    
    def get_measurement_operator(self, basis: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get measurement operators for given basis.
        
        Args:
            basis: 0 (rectilinear) or 1 (diagonal)
        
        Returns:
            Tuple of (M0, M1) measurement operators
        """
        if basis == 0:  # Rectilinear basis
            # M0 = |0⟩⟨0|
            M0 = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
            # M1 = |1⟩⟨1|
            M1 = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)
        else:  # Diagonal basis
            # M0 = |+⟩⟨+|
            M0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
            # M1 = |-⟩⟨-|
            M1 = np.array([[0.5, -0.5], [-0.5, 0.5]], dtype=complex)
        
        return M0, M1
    
    def apply_noise(self, state: np.ndarray, noise_level: float = 0.01) -> np.ndarray:
        """
        Apply noise to quantum state.
        
        Args:
            state: Input quantum state
            noise_level: Amount of noise to apply
        
        Returns:
            Noisy state
        """
        if self.noise_model == 'depolarizing':
            # Depolarizing noise: mix with maximally mixed state
            mixed_state = np.array([0.5, 0.5], dtype=complex)
            noisy_state = (1 - noise_level) * state + noise_level * mixed_state
            # Renormalize
            noisy_state = noisy_state / np.linalg.norm(noisy_state)
            return noisy_state
        elif self.noise_model == 'amplitude_damping':
            # Simplified amplitude damping
            decay_factor = 1 - noise_level
            noisy_state = state.copy()
            noisy_state[0] += np.sqrt(noise_level) * state[1]
            noisy_state[1] *= np.sqrt(decay_factor)
            noisy_state = noisy_state / np.linalg.norm(noisy_state)
            return noisy_state
        else:
            return state
    
    def measure_qubit(
        self, 
        state: np.ndarray, 
        basis: int,
        noise_level: float = 0.0
    ) -> int:
        """
        Measure a qubit in given basis.
        
        Args:
            state: Quantum state to measure
            basis: Measurement basis
            noise_level: Channel noise level
        
        Returns:
            Measurement result (0 or 1)
        """
        # Apply noise if specified
        if noise_level > 0:
            state = self.apply_noise(state, noise_level)
        
        # Get measurement operators
        M0, M1 = self.get_measurement_operator(basis)
        
        # Calculate probabilities
        prob_0 = np.abs(np.vdot(state, M0 @ state))
        prob_1 = np.abs(np.vdot(state, M1 @ state))
        
        # Normalize probabilities
        total = prob_0 + prob_1
        prob_0 /= total
        prob_1 /= total
        
        # Measure
        result = np.random.choice([0, 1], p=[prob_0, prob_1])
        return result
    
    def simulate_qkd_exchange(
        self,
        alice_bits: List[int],
        alice_bases: List[int],
        bob_bases: List[int],
        noise_level: float = 0.01
    ) -> List[int]:
        """
        Simulate quantum key distribution exchange.
        
        Args:
            alice_bits: Alice's random bits
            alice_bases: Alice's random bases
            bob_bases: Bob's random bases
            noise_level: Quantum channel noise
        
        Returns:
            Bob's measurement results
        """
        bob_results = []
        
        for alice_bit, alice_basis, bob_basis in zip(alice_bits, alice_bases, bob_bases):
            # Alice prepares qubit
            state = self.create_qubit_state(alice_bit, alice_basis)
            
            # Bob measures qubit
            result = self.measure_qubit(state, bob_basis, noise_level)
            bob_results.append(result)
        
        logger.debug(f"Simulated {len(alice_bits)} qubit exchanges")
        return bob_results
    
    def estimate_channel_quality(
        self,
        n_test_qubits: int = 1000,
        noise_level: float = 0.01
    ) -> dict:
        """
        Estimate quantum channel quality.
        
        Args:
            n_test_qubits: Number of test qubits to send
            noise_level: Expected noise level
        
        Returns:
            Dictionary with channel statistics
        """
        # Test with matching bases (should have low error)
        alice_bits = np.random.randint(0, 2, n_test_qubits)
        bases = np.random.randint(0, 2, n_test_qubits)
        
        bob_results = self.simulate_qkd_exchange(
            alice_bits.tolist(),
            bases.tolist(),
            bases.tolist(),
            noise_level
        )
        
        # Calculate error rate
        errors = sum(1 for a, b in zip(alice_bits, bob_results) if a != b)
        error_rate = errors / n_test_qubits
        
        # Calculate fidelity (simplified)
        fidelity = 1 - error_rate
        
        stats = {
            "error_rate": error_rate,
            "fidelity": fidelity,
            "test_qubits": n_test_qubits,
            "noise_level": noise_level,
            "status": "good" if error_rate < 0.11 else "degraded"
        }
        
        logger.info(f"Channel quality: error_rate={error_rate:.4f}, fidelity={fidelity:.4f}")
        return stats

