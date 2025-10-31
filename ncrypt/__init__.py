"""
nCrypt: Quantum-Resistant Blockchain SDK
A comprehensive SDK demonstrating the NCRYPT whitepaper concepts:
- Quantum-resistant cryptography (Module-LWE/SIS)
- Multi-tier privacy (Transparent, Private, Accountable)
- DAPOA framework (Decentralized Anonymous Payment with Optional Accountability)
- Quantum key distribution (BB84)
"""

__version__ = "1.0.0"
__author__ = "nCrypt Team"

# Core quantum cryptography
from .core.qkd import BB84Protocol
from .core.encryption import QuantumEncryption

# Post-quantum lattice-based cryptography
from .lattice.post_quantum import ModuleLWE, ModuleSIS, LatticeCrypto

# Multi-tier privacy transactions
from .transactions.privacy_modes import (
    DAPOAFramework, PrivacyMode, Transaction,
    TransparentTransaction, PrivateTransaction, AccountableTransaction
)

# Simulators and utilities
from .simulator.quantum_simulator import QuantumSimulator
from .utils.key_manager import KeyManager

__all__ = [
    # Quantum cryptography
    "BB84Protocol",
    "QuantumEncryption",
    
    # Post-quantum cryptography
    "ModuleLWE",
    "ModuleSIS",
    "LatticeCrypto",
    
    # Privacy framework
    "DAPOAFramework",
    "PrivacyMode",
    "Transaction",
    "TransparentTransaction",
    "PrivateTransaction",
    "AccountableTransaction",
    
    # Utilities
    "QuantumSimulator",
    "KeyManager",
]

