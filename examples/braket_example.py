"""
AWS Braket integration example.

This example demonstrates using AWS Braket for quantum key distribution.
Note: Requires AWS credentials and amazon-braket-sdk installed.
"""

import logging
from ncrypt.braket.quantum_backend import BraketBackend, BraketQKD

# Configure logging
logging.basicConfig(level=logging.INFO)


def main():
    print("=" * 60)
    print("nCrypt: AWS Braket Integration Demo")
    print("=" * 60)
    
    # Option 1: Use local Braket simulator (free, no AWS account needed)
    print("\n1. Using Braket Local Simulator...")
    
    try:
        backend = BraketBackend(use_local_simulator=True)
        device_info = backend.get_device_info()
        print(f"✅ Device: {device_info['name']}")
        print(f"   Type: {device_info['type']}")
        
        # Run BB84 protocol
        qkd = BraketQKD(backend)
        result = qkd.run_bb84(n_bits=500, error_threshold=0.11)
        
        if result:
            print(f"\n✅ QKD completed on Braket!")
            print(f"   Final key length: {result['key_length']} bits")
            print(f"   Error rate: {result['error_rate']:.4f}")
            print(f"   Device: {result['device']}")
        else:
            print("\n❌ QKD failed!")
        
    except ImportError as e:
        print("\n❌ AWS Braket SDK not installed!")
        print("   Install with: pip install amazon-braket-sdk")
        return
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    # Option 2: Use real quantum device (requires AWS account and credits)
    # Uncomment to use a real device:
    """
    print("\n2. Using Real Quantum Device...")
    device_arn = "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1"
    
    backend_real = BraketBackend(device_arn=device_arn, use_local_simulator=False)
    device_info = backend_real.get_device_info()
    
    print(f"✅ Device: {device_info['name']}")
    print(f"   Provider: {device_info['provider']}")
    print(f"   Status: {device_info['status']}")
    
    # Estimate cost
    n_circuits = 500
    cost_estimate = backend_real.estimate_cost(n_circuits)
    print(f"\n💰 Cost Estimate:")
    print(f"   Circuits: {n_circuits}")
    print(f"   Total: ${cost_estimate['total_cost']} {cost_estimate['currency']}")
    print(f"   Note: {cost_estimate['note']}")
    
    # Run QKD (uncomment to actually run on device)
    # qkd_real = BraketQKD(backend_real)
    # result = qkd_real.run_bb84(n_bits=500)
    """
    
    print("\n" + "=" * 60)
    print("Braket demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

