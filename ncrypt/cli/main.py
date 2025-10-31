"""
nCrypt CLI
Command-line interface for quantum cryptography operations.
"""

import click
import yaml
import logging
import sys
from pathlib import Path
from typing import Optional

from ncrypt.core.qkd import BB84Protocol
from ncrypt.core.encryption import QuantumEncryption
from ncrypt.simulator.quantum_simulator import QuantumSimulator
from ncrypt.utils.key_manager import KeyManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to config.yaml')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """nCrypt: Quantum Cryptography SDK"""
    ctx.ensure_object(dict)
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if config:
        ctx.obj['config'] = load_config(config)
    else:
        ctx.obj['config'] = {}


@cli.command()
@click.option('--bits', '-n', default=2000, help='Number of qubits to exchange (default: 2000 for 256+ bit keys)')
@click.option('--noise', '-e', default=0.01, help='Channel noise level (0.0-0.5)')
@click.option('--key-id', '-k', required=True, help='Key identifier for storage')
@click.option('--backend', '-b', type=click.Choice(['simulator', 'braket']), default='simulator')
@click.option('--device-arn', help='AWS Braket device ARN (for braket backend)')
@click.pass_context
def generate_key(ctx, bits, noise, key_id, backend, device_arn):
    """Generate quantum key using BB84 protocol."""
    click.echo(f"Generating quantum key with {bits} qubits...")
    click.echo(f"Backend: {backend}")
    
    # Warn if bits might be too low
    if bits < 1500:
        click.echo(f"⚠️  Warning: {bits} qubits may produce a key too short for encryption")
        click.echo(f"   Recommended: at least 2000 qubits for 256-bit keys")
    
    try:
        if backend == 'simulator':
            # Use simulator
            protocol = BB84Protocol()
            result = protocol.run_protocol(n_bits=bits, noise_level=noise)
            
            if result is None:
                click.echo("❌ Key generation failed: error rate too high", err=True)
                sys.exit(1)
            
            key = result.final_key
            metadata = {
                "protocol": "BB84",
                "backend": "simulator",
                "noise_level": noise,
                "error_rate": result.error_rate,
                "raw_bits": bits
            }
        
        elif backend == 'braket':
            # Use AWS Braket
            try:
                from ncrypt.braket.quantum_backend import BraketBackend, BraketQKD
            except ImportError:
                click.echo("❌ AWS Braket SDK not installed", err=True)
                click.echo("Install with: pip install amazon-braket-sdk", err=True)
                sys.exit(1)
            
            if device_arn:
                braket_backend = BraketBackend(device_arn=device_arn, use_local_simulator=False)
            else:
                braket_backend = BraketBackend(use_local_simulator=True)
            
            qkd = BraketQKD(braket_backend)
            result = qkd.run_bb84(n_bits=bits)
            
            if result is None:
                click.echo("❌ Key generation failed", err=True)
                sys.exit(1)
            
            key = result["final_key"]
            metadata = {
                "protocol": "BB84",
                "backend": "braket",
                "device": result["device"],
                "error_rate": result["error_rate"],
                "raw_bits": bits
            }
        
        # Save key
        config = ctx.obj.get('config', {})
        storage_dir = config.get('key_storage', './keys')
        key_manager = KeyManager(storage_dir)
        key_manager.save_key(key, key_id, metadata)
        
        click.echo(f"✅ Key generated successfully!")
        click.echo(f"   Key ID: {key_id}")
        click.echo(f"   Length: {len(key)} bits")
        click.echo(f"   Error rate: {metadata['error_rate']:.4f}")
        
        # Check if key is long enough for encryption
        if len(key) < 256:
            click.echo(f"\n⚠️  Note: Key is {len(key)} bits (< 256 bits)")
            click.echo(f"   This key is too short for AES-256 encryption")
            click.echo(f"   Generate a new key with more qubits (try --bits 2000)")
        else:
            click.echo(f"\n✅ Key is sufficient for AES-256 encryption ({len(key)} >= 256 bits)")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--key-id', '-k', required=True, help='Key identifier')
@click.pass_context
def show_key(ctx, key_id):
    """Show key information."""
    try:
        config = ctx.obj.get('config', {})
        storage_dir = config.get('key_storage', './keys')
        key_manager = KeyManager(storage_dir)
        
        info = key_manager.get_key_info(key_id)
        
        click.echo(f"\nKey Information:")
        click.echo(f"  ID: {info['key_id']}")
        click.echo(f"  Length: {info['key_length']} bits")
        click.echo(f"  Created: {info['timestamp']}")
        click.echo(f"  Protocol: {info.get('protocol', 'N/A')}")
        click.echo(f"  Backend: {info.get('backend', 'N/A')}")
        if 'error_rate' in info:
            click.echo(f"  Error Rate: {info['error_rate']:.4f}")
        
    except FileNotFoundError:
        click.echo(f"❌ Key not found: {key_id}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def list_keys(ctx):
    """List all stored keys."""
    try:
        config = ctx.obj.get('config', {})
        storage_dir = config.get('key_storage', './keys')
        key_manager = KeyManager(storage_dir)
        
        keys = key_manager.list_keys()
        
        if not keys:
            click.echo("No keys found.")
            return
        
        click.echo(f"\nStored Keys ({len(keys)}):")
        click.echo("-" * 80)
        
        for key_info in keys:
            click.echo(f"  {key_info['key_id']:20s} | {key_info['key_length']:6d} bits | {key_info['timestamp'][:19]}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--key-id', '-k', required=True, help='Key identifier')
@click.option('--input', '-i', required=True, type=click.Path(exists=True), help='Input file')
@click.option('--output', '-o', required=True, type=click.Path(), help='Output file')
@click.pass_context
def encrypt(ctx, key_id, input, output):
    """Encrypt file using quantum key."""
    try:
        config = ctx.obj.get('config', {})
        storage_dir = config.get('key_storage', './keys')
        key_manager = KeyManager(storage_dir)
        
        # Load key
        key_data = key_manager.load_key(key_id)
        quantum_key = key_data["key"]
        
        # Encrypt
        qe = QuantumEncryption()
        iv, tag = qe.encrypt_file(input, output, quantum_key)
        
        # Save IV and tag
        metadata_file = f"{output}.meta"
        with open(metadata_file, 'w') as f:
            yaml.dump({
                'iv': iv.hex(),
                'tag': tag.hex(),
                'key_id': key_id
            }, f)
        
        click.echo(f"✅ File encrypted successfully!")
        click.echo(f"   Input: {input}")
        click.echo(f"   Output: {output}")
        click.echo(f"   Metadata: {metadata_file}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--key-id', '-k', help='Key identifier (or read from metadata)')
@click.option('--input', '-i', required=True, type=click.Path(exists=True), help='Encrypted file')
@click.option('--output', '-o', required=True, type=click.Path(), help='Output file')
@click.option('--metadata', '-m', type=click.Path(exists=True), help='Metadata file')
@click.pass_context
def decrypt(ctx, key_id, input, output, metadata):
    """Decrypt file using quantum key."""
    try:
        config = ctx.obj.get('config', {})
        storage_dir = config.get('key_storage', './keys')
        key_manager = KeyManager(storage_dir)
        
        # Load metadata
        if metadata:
            metadata_file = metadata
        else:
            metadata_file = f"{input}.meta"
        
        with open(metadata_file, 'r') as f:
            meta = yaml.safe_load(f)
        
        iv = bytes.fromhex(meta['iv'])
        tag = bytes.fromhex(meta['tag'])
        
        if not key_id:
            key_id = meta.get('key_id')
            if not key_id:
                raise ValueError("Key ID not specified and not found in metadata")
        
        # Load key
        key_data = key_manager.load_key(key_id)
        quantum_key = key_data["key"]
        
        # Decrypt
        qe = QuantumEncryption()
        qe.decrypt_file(input, output, iv, tag, quantum_key)
        
        click.echo(f"✅ File decrypted successfully!")
        click.echo(f"   Input: {input}")
        click.echo(f"   Output: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--bits', '-n', default=1000, help='Number of test qubits')
@click.option('--noise', '-e', default=0.01, help='Channel noise level')
def test_channel(bits, noise):
    """Test quantum channel quality."""
    click.echo(f"Testing quantum channel...")
    
    try:
        simulator = QuantumSimulator()
        stats = simulator.estimate_channel_quality(n_test_qubits=bits, noise_level=noise)
        
        click.echo(f"\nChannel Quality Report:")
        click.echo(f"  Test Qubits: {stats['test_qubits']}")
        click.echo(f"  Error Rate: {stats['error_rate']:.4f}")
        click.echo(f"  Fidelity: {stats['fidelity']:.4f}")
        click.echo(f"  Status: {stats['status'].upper()}")
        
        if stats['status'] == 'good':
            click.echo(f"\n✅ Channel quality is good for QKD")
        else:
            click.echo(f"\n⚠️  Channel quality is degraded")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def init_config():
    """Initialize config.yaml file."""
    config = {
        'key_storage': './keys',
        'bb84': {
            'default_bits': 1000,
            'noise_level': 0.01,
            'error_threshold': 0.11
        },
        'encryption': {
            'algorithm': 'AES-256-CBC'
        },
        'braket': {
            'use_local_simulator': True,
            'device_arn': None,
            'aws_profile': 'default'
        }
    }
    
    config_path = Path('./config.yaml')
    if config_path.exists():
        click.confirm('config.yaml already exists. Overwrite?', abort=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    click.echo(f"✅ Created config.yaml")


def main():
    """Entry point for CLI."""
    cli(obj={})


if __name__ == '__main__':
    main()

