"""
AWS Braket Quantum Backend
Integration with AWS Braket for running on real quantum devices.
"""

from typing import List, Dict, Optional, Tuple
import logging

try:
    from braket.circuits import Circuit
    from braket.devices import LocalSimulator
    from braket.aws import AwsDevice
    BRAKET_AVAILABLE = True
except ImportError:
    BRAKET_AVAILABLE = False
    Circuit = None
    LocalSimulator = None
    AwsDevice = None

logger = logging.getLogger(__name__)


class BraketBackend:
    """
    AWS Braket backend for quantum operations.
    
    Supports both local simulation and real quantum devices through AWS Braket.
    
    Supported Quantum Devices:
        - IonQ Forte: Trapped ion system with 36 qubits (#AQ 36)
          ARN: arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1
          Specs: 0.4% 2-qubit gate error, all-to-all connectivity
          Cost: ~$38 per key generation
          Docs: https://ionq.com/quantum-systems/forte
          
        - Rigetti Ankaa-3: Superconducting system with 82 qubits
          ARN: arn:aws:braket:us-west-1::device/qpu/rigetti/Ankaa-3
          Specs: Square lattice, tunable couplers
          Cost: ~$30 per key generation
          Docs: https://qcs.rigetti.com/qpus
          
        - Local Simulator: Free, for development and testing only
          Note: Not quantum-secure, uses pseudorandom numbers
    
    References:
        AWS Braket: https://docs.aws.amazon.com/braket/
    """
    
    def __init__(
        self,
        device_arn: Optional[str] = None,
        use_local_simulator: bool = True,
        aws_session: Optional[object] = None
    ):
        """
        Initialize Braket backend.
        
        Args:
            device_arn: ARN of AWS quantum device. Examples:
                - IonQ Forte: 'arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1'
                - Rigetti Ankaa-3: 'arn:aws:braket:us-west-1::device/qpu/rigetti/Ankaa-3'
            use_local_simulator: Use local Braket simulator if True (not quantum-secure)
            aws_session: Optional AWS session for device access
            
        References:
            Device documentation:
            - IonQ: https://ionq.com/quantum-systems/forte
            - Rigetti: https://qcs.rigetti.com/qpus
        """
        if not BRAKET_AVAILABLE:
            raise ImportError(
                "AWS Braket SDK not installed. "
                "Install with: pip install amazon-braket-sdk"
            )
        
        self.device_arn = device_arn
        self.use_local_simulator = use_local_simulator
        self.aws_session = aws_session
        
        if use_local_simulator:
            self.device = LocalSimulator()
            logger.info("Using Braket local simulator")
        elif device_arn:
            self.device = AwsDevice(device_arn, aws_session=aws_session)
            logger.info(f"Using AWS Braket device: {device_arn}")
        else:
            raise ValueError("Must specify device_arn or use_local_simulator")
    
    def create_bb84_circuit(
        self,
        bit: int,
        basis: int,
        measure_basis: int
    ) -> Circuit:
        """
        Create BB84 protocol circuit.
        
        Args:
            bit: Bit to encode (0 or 1)
            basis: Encoding basis (0=rectilinear, 1=diagonal)
            measure_basis: Measurement basis
        
        Returns:
            Braket Circuit
        """
        circuit = Circuit()
        
        # Prepare qubit based on bit and basis
        if basis == 0:  # Rectilinear basis
            if bit == 1:
                circuit.x(0)  # Apply X gate for |1⟩
        else:  # Diagonal basis
            circuit.h(0)  # Apply Hadamard for |+⟩ or |-⟩
            if bit == 1:
                circuit.z(0)  # Apply Z gate for |-⟩
        
        # Measure in chosen basis
        if measure_basis == 1:  # Diagonal basis measurement
            circuit.h(0)  # Apply Hadamard before measurement
        
        # Perform measurement
        circuit.measure(0)
        
        return circuit
    
    def run_qkd_exchange(
        self,
        alice_bits: List[int],
        alice_bases: List[int],
        bob_bases: List[int],
        shots: int = 1
    ) -> List[int]:
        """
        Run QKD exchange on Braket device.
        
        Args:
            alice_bits: Alice's random bits
            alice_bases: Alice's random bases
            bob_bases: Bob's random bases
            shots: Number of shots per circuit (usually 1 for QKD)
        
        Returns:
            Bob's measurement results
        """
        results = []
        
        logger.info(f"Running {len(alice_bits)} QKD exchanges on Braket device")
        
        for bit, alice_basis, bob_basis in zip(alice_bits, alice_bases, bob_bases):
            # Create circuit
            circuit = self.create_bb84_circuit(bit, alice_basis, bob_basis)
            
            # Run on device
            task = self.device.run(circuit, shots=shots)
            result = task.result()
            
            # Get measurement result
            measurements = result.measurements
            measured_bit = int(measurements[0][0])
            results.append(measured_bit)
        
        logger.info(f"Completed {len(results)} QKD exchanges")
        return results
    
    def run_batch_qkd(
        self,
        alice_bits: List[int],
        alice_bases: List[int],
        bob_bases: List[int],
        batch_size: int = 100
    ) -> List[int]:
        """
        Run QKD in batches to optimize device usage.
        
        Args:
            alice_bits: Alice's random bits
            alice_bases: Alice's random bases
            bob_bases: Bob's random bases
            batch_size: Number of circuits to run in parallel
        
        Returns:
            Bob's measurement results
        """
        all_results = []
        n_bits = len(alice_bits)
        
        for i in range(0, n_bits, batch_size):
            end_idx = min(i + batch_size, n_bits)
            batch_bits = alice_bits[i:end_idx]
            batch_alice_bases = alice_bases[i:end_idx]
            batch_bob_bases = bob_bases[i:end_idx]
            
            batch_results = self.run_qkd_exchange(
                batch_bits,
                batch_alice_bases,
                batch_bob_bases
            )
            all_results.extend(batch_results)
            
            logger.debug(f"Batch {i//batch_size + 1}: {len(batch_results)} exchanges")
        
        return all_results
    
    def get_device_info(self) -> Dict:
        """
        Get information about the quantum device.
        
        Returns:
            Dictionary with device information
        """
        if self.use_local_simulator:
            return {
                "name": "Local Simulator",
                "type": "simulator",
                "provider": "Amazon Braket"
            }
        else:
            properties = self.device.properties
            return {
                "name": properties.provider.name,
                "type": properties.type,
                "provider": properties.provider.provider,
                "status": self.device.status,
                "arn": self.device_arn
            }
    
    def estimate_cost(self, n_circuits: int) -> Dict:
        """
        Estimate cost of running circuits on AWS Braket.
        
        Args:
            n_circuits: Number of circuits to run
        
        Returns:
            Cost estimate dictionary
        """
        if self.use_local_simulator:
            return {
                "total_cost": 0.0,
                "currency": "USD",
                "note": "Local simulator is free"
            }
        
        # AWS Braket pricing (approximate, as of 2024)
        # This varies by device - check current AWS pricing
        if "ionq" in self.device_arn.lower():
            cost_per_task = 0.30
            cost_per_shot = 0.01
        elif "rigetti" in self.device_arn.lower():
            cost_per_task = 0.30
            cost_per_shot = 0.00035
        else:
            cost_per_task = 0.30
            cost_per_shot = 0.001
        
        total_cost = (cost_per_task + cost_per_shot) * n_circuits
        
        return {
            "total_cost": round(total_cost, 2),
            "cost_per_task": cost_per_task,
            "cost_per_shot": cost_per_shot,
            "currency": "USD",
            "n_circuits": n_circuits,
            "note": "Estimate only - check AWS Braket pricing for exact costs"
        }


class BraketQKD:
    """
    Quantum Key Distribution using AWS Braket.
    
    High-level interface for running BB84 protocol on Braket devices.
    """
    
    def __init__(self, backend: BraketBackend):
        """
        Initialize Braket QKD.
        
        Args:
            backend: Configured BraketBackend instance
        """
        self.backend = backend
        logger.info("BraketQKD initialized")
    
    def run_bb84(
        self,
        n_bits: int = 1000,
        error_threshold: float = 0.11
    ) -> Optional[Dict]:
        """
        Run BB84 protocol on Braket device.
        
        Args:
            n_bits: Number of qubits to exchange
            error_threshold: Maximum acceptable error rate
        
        Returns:
            Dictionary with QKD results or None if failed
        """
        import numpy as np
        
        logger.info(f"Starting BB84 protocol on Braket with {n_bits} qubits")
        
        # Generate random bits and bases
        alice_bits = np.random.randint(0, 2, n_bits).tolist()
        alice_bases = np.random.randint(0, 2, n_bits).tolist()
        bob_bases = np.random.randint(0, 2, n_bits).tolist()
        
        # Run quantum exchange
        bob_bits = self.backend.run_batch_qkd(alice_bits, alice_bases, bob_bases)
        
        # Sift keys (keep only matching bases)
        sifted_alice = []
        sifted_bob = []
        for a_bit, a_basis, b_bit, b_basis in zip(
            alice_bits, alice_bases, bob_bits, bob_bases
        ):
            if a_basis == b_basis:
                sifted_alice.append(a_bit)
                sifted_bob.append(b_bit)
        
        if len(sifted_alice) == 0:
            logger.error("No matching bases found")
            return None
        
        # Estimate error rate
        sample_size = len(sifted_alice) // 2
        errors = sum(
            1 for i in range(sample_size)
            if sifted_alice[i] != sifted_bob[i]
        )
        error_rate = errors / sample_size
        
        if error_rate > error_threshold:
            logger.warning(f"Error rate {error_rate:.4f} exceeds threshold")
            return None
        
        # Use remaining bits as key
        final_key = sifted_alice[sample_size:]
        
        result = {
            "final_key": final_key,
            "key_length": len(final_key),
            "error_rate": error_rate,
            "sifted_bits": len(sifted_alice),
            "raw_bits": n_bits,
            "device": self.backend.get_device_info()["name"]
        }
        
        logger.info(f"BB84 completed. Key length: {len(final_key)}, QBER: {error_rate:.4f}")
        return result

