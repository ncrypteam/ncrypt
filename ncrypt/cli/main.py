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
from ncrypt.utils.aws_pricing import BraketPricing

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
@click.option('--dry-run', is_flag=True, help='Show what would be executed without running')
@click.pass_context
def generate_key(ctx, bits, noise, key_id, backend, device_arn, dry_run):
    """Generate quantum key using BB84 protocol."""
    
    if dry_run:
        click.echo(f"🔍 DRY RUN: Simulating operation (not executing)\n")
    
    click.echo(f"Generating quantum key with {bits} qubits...")
    click.echo(f"Backend: {backend}")
    
    # Calculate exact resource usage
    click.echo(f"\n📊 Resource Calculation:")
    click.echo(f"   Raw qubits to exchange: {bits}")
    click.echo(f"   Expected sifted key: ~{bits // 2} bits (50% basis matching)")
    click.echo(f"   Expected final key: ~{int(bits * 0.175)} bits (after error check & amplification)")
    
    if backend == 'braket' and device_arn:
        # Calculate exact AWS costs using real-time pricing
        click.echo(f"\n💰 AWS Braket Resource Usage:")
        click.echo(f"   Number of circuits: {bits}")
        click.echo(f"   Shots per circuit: 1")
        click.echo(f"   Total quantum tasks: {bits}")
        
        # Get real-time pricing from AWS
        pricer = BraketPricing()
        device_type = 'ionq' if 'ionq' in device_arn.lower() else 'rigetti'
        cost_info = pricer.calculate_cost(bits, device_type, shots_per_circuit=1)
        
        click.echo(f"   Estimated cost: ${cost_info['total_cost']:.2f}")
        if cost_info['pricing_source'] == 'AWS Pricing API':
            click.echo(f"   (Real-time pricing from AWS)")
        else:
            click.echo(f"   (Fallback pricing - AWS API unavailable)")
        
        if cost_info['total_cost'] > 100:
            click.echo(f"\n⚠️  HIGH COST WARNING: ${cost_info['total_cost']:.2f}")
            click.echo(f"   Consider reducing --bits or using simulator")
            if not dry_run:
                if not click.confirm(f"\n   Proceed with ${cost_info['total_cost']:.2f} charge?"):
                    click.echo("Cancelled by user")
                    sys.exit(0)
    
    if dry_run:
        click.echo(f"\n✅ Dry run complete. No operations executed.")
        click.echo(f"   Remove --dry-run flag to actually generate the key")
        return
    
    # Warn if bits might be too low
    if bits < 1500:
        click.echo(f"\n⚠️  Warning: {bits} qubits may produce a key too short for encryption")
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
@click.option('--profile', '-p', default='default', help='AWS profile')
def show_pricing(profile):
    """
    Show current AWS Braket pricing (fetches from AWS Pricing API).
    
    Displays real-time pricing for:
    - IonQ Forte (36 qubits): https://ionq.com/quantum-systems/forte
    - Rigetti Ankaa-3 (82 qubits): https://qcs.rigetti.com/qpus
    """
    click.echo("💰 AWS Braket Pricing Information\n")
    
    pricer = BraketPricing(aws_profile=profile)
    
    # Try to fetch pricing for all devices
    click.echo("Fetching pricing from AWS Pricing API...\n")
    
    all_pricing = pricer.get_all_pricing()
    
    click.echo("=" * 60)
    for device_type, pricing in all_pricing.items():
        click.echo(f"\n{pricing['name'].upper()}")
        click.echo(f"  Task cost: ${pricing['task']}")
        click.echo(f"  Shot cost: ${pricing['shot']}")
        
        if pricing.get('source') == 'AWS Pricing API':
            click.echo(f"  Source: 📡 AWS Pricing API (real-time)")
        else:
            click.echo(f"  Source: ℹ️  Fallback (updated late 2024)")
        
        # Example costs
        example_circuits = 100
        example_cost = (pricing['task'] + pricing['shot']) * example_circuits
        click.echo(f"  Example: {example_circuits} circuits = ${example_cost:.2f}")
    
    click.echo("\n" + "=" * 60)
    click.echo("\n💡 Tips:")
    click.echo("  - Rigetti is ~28x cheaper per shot than IonQ")
    click.echo("  - Simulator is always FREE")
    click.echo("  - Pricing updates automatically from AWS when available")
    click.echo("\n  To check costs: ncrypt estimate-cost --bits <N> --device <TYPE>")


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


@cli.command()
@click.option('--month', '-m', help='Month in YYYY-MM format (default: current month)')
@click.option('--profile', '-p', default='default', help='AWS profile to use')
@click.option('--region', '-r', default='us-east-1', help='AWS region')
def check_aws_costs(month, profile, region):
    """Check AWS Braket costs using real AWS billing data."""
    import subprocess
    import json
    from datetime import datetime, timedelta
    
    click.echo("💰 Checking AWS Braket costs...\n")
    
    # Determine time period
    if month:
        try:
            start_date = datetime.strptime(month, '%Y-%m')
            # Last day of month
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1)
            
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
        except ValueError:
            click.echo("❌ Invalid month format. Use YYYY-MM (e.g., 2024-11)", err=True)
            sys.exit(1)
    else:
        # Current month
        now = datetime.now()
        start_date = now.replace(day=1)
        today = now
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = today.strftime('%Y-%m-%d')
    
    click.echo(f"📅 Period: {start_str} to {end_str}")
    
    # Check if AWS CLI is installed
    try:
        subprocess.run(['aws', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("❌ AWS CLI not installed!", err=True)
        click.echo("   Install: pip install awscli", err=True)
        click.echo("   Configure: aws configure", err=True)
        sys.exit(1)
    
    # Check AWS credentials
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity', '--profile', profile],
            capture_output=True,
            text=True,
            check=True
        )
        identity = json.loads(result.stdout)
        click.echo(f"✅ AWS Account: {identity['Account']}")
        click.echo(f"   User/Role: {identity['Arn'].split('/')[-1]}\n")
    except subprocess.CalledProcessError as e:
        click.echo("❌ AWS credentials not configured or invalid!", err=True)
        click.echo(f"   Error: {e.stderr}", err=True)
        click.echo("\n   Run: aws configure --profile " + profile, err=True)
        sys.exit(1)
    
    # Get Braket costs
    try:
        # Query specifically for Amazon Braket service
        cmd_braket = [
            'aws', 'ce', 'get-cost-and-usage',
            '--time-period', f'Start={start_str},End={end_str}',
            '--granularity', 'MONTHLY',
            '--metrics', 'BlendedCost',
            '--filter', json.dumps({"Dimensions": {"Key": "SERVICE", "Values": ["Amazon Braket"]}}),
            '--profile', profile
        ]
        
        result = subprocess.run(cmd_braket, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Parse Braket costs
        braket_cost = 0.0
        if 'ResultsByTime' in data and data['ResultsByTime']:
            for time_period in data['ResultsByTime']:
                cost = float(time_period['Total']['BlendedCost']['Amount'])
                braket_cost += cost
        
        click.echo(f"🔬 Amazon Braket")
        click.echo(f"   Cost: ${braket_cost:.2f}")
        
        # Get total AWS costs (all services)
        cmd_total = [
            'aws', 'ce', 'get-cost-and-usage',
            '--time-period', f'Start={start_str},End={end_str}',
            '--granularity', 'MONTHLY',
            '--metrics', 'BlendedCost',
            '--profile', profile
        ]
        
        result_total = subprocess.run(cmd_total, capture_output=True, text=True, check=True)
        data_total = json.loads(result_total.stdout)
        
        total_cost = 0.0
        if 'ResultsByTime' in data_total and data_total['ResultsByTime']:
            for time_period in data_total['ResultsByTime']:
                cost = float(time_period['Total']['BlendedCost']['Amount'])
                total_cost += cost
        
        click.echo(f"\n💵 Total Braket Cost: ${braket_cost:.2f}")
        click.echo(f"💵 Total AWS Cost (all services): ${total_cost:.2f}")
        
        if braket_cost == 0.0:
            click.echo("\n✅ No Braket charges found (using local simulator or no usage)")
        elif braket_cost < 10.0:
            click.echo("\n✅ Costs are low")
        elif braket_cost < 50.0:
            click.echo("\n⚠️  Moderate costs - monitor usage")
        else:
            click.echo("\n⚠️  HIGH COSTS - review quantum device usage!")
        
    except subprocess.CalledProcessError as e:
        click.echo("❌ Failed to get cost data from AWS", err=True)
        click.echo(f"   Error: {e.stderr}", err=True)
        sys.exit(1)
    except json.JSONDecodeError:
        click.echo("❌ Failed to parse AWS response", err=True)
        sys.exit(1)


@cli.command()
@click.option('--bits', '-n', type=int, required=True, help='Number of qubits for key generation')
@click.option('--device-arn', help='AWS Braket device ARN')
@click.option('--runs', '-r', type=int, default=1, help='Number of simulation runs for accuracy')
def plan_execution(bits, device_arn, runs):
    """Plan quantum operation with exact resource calculation using simulator."""
    click.echo(f"📋 EXECUTION PLAN\n")
    click.echo(f"Operation: BB84 Quantum Key Distribution")
    click.echo(f"Input qubits: {bits}")
    click.echo("=" * 60)
    
    # Run on simulator multiple times to get accurate statistics
    click.echo(f"\n🔬 Running {runs} simulation(s) to calculate exact resources...")
    
    from ncrypt.core.qkd import BB84Protocol
    protocol = BB84Protocol()
    
    results = []
    for i in range(runs):
        result = protocol.run_protocol(n_bits=bits, noise_level=0.01)
        if result:
            results.append({
                'sifted': len(result.sifted_key),
                'final': result.key_length,
                'error_rate': result.error_rate
            })
    
    if not results:
        click.echo("❌ Simulation failed")
        return
    
    # Calculate averages
    avg_sifted = sum(r['sifted'] for r in results) / len(results)
    avg_final = sum(r['final'] for r in results) / len(results)
    avg_error = sum(r['error_rate'] for r in results) / len(results)
    
    min_final = min(r['final'] for r in results)
    max_final = max(r['final'] for r in results)
    
    click.echo(f"\n📊 Simulated Results ({runs} run{'s' if runs > 1 else ''}):")
    click.echo(f"   Average sifted key: {avg_sifted:.0f} bits")
    click.echo(f"   Average final key: {avg_final:.0f} bits")
    click.echo(f"   Final key range: {min_final}-{max_final} bits")
    click.echo(f"   Average error rate: {avg_error:.4f}")
    
    if avg_final < 256:
        click.echo(f"\n⚠️  Expected key ({avg_final:.0f} bits) is too short for AES-256!")
        click.echo(f"   Recommended: {int(256 / 0.175)} qubits for 256+ bit key")
    else:
        click.echo(f"\n✅ Expected key ({avg_final:.0f} bits) is sufficient for encryption")
    
    # AWS Resource calculation
    if device_arn:
        click.echo(f"\n💰 AWS Braket Resources (Real Device):")
        click.echo(f"   Device: {device_arn.split('/')[-1]}")
        click.echo(f"   Circuits to execute: {bits}")
        click.echo(f"   Shots per circuit: 1")
        click.echo(f"   Total tasks: {bits}")
        
        # Get real-time pricing from AWS
        from ncrypt.utils.aws_pricing import BraketPricing
        pricer = BraketPricing()
        device_type = 'ionq' if 'ionq' in device_arn.lower() else 'rigetti'
        cost_info = pricer.calculate_cost(bits, device_type, shots_per_circuit=1)
        
        click.echo(f"\n   Task costs: ${cost_info['unit_task_cost']} × {bits} = ${cost_info['task_cost']:.2f}")
        click.echo(f"   Shot costs: ${cost_info['unit_shot_cost']} × {bits} = ${cost_info['shot_cost']:.2f}")
        click.echo(f"   {'─' * 50}")
        click.echo(f"   TOTAL COST: ${cost_info['total_cost']:.2f}")
        
        if cost_info['pricing_source'] == 'AWS Pricing API':
            click.echo(f"   📡 Real-time pricing from AWS")
        else:
            click.echo(f"   ℹ️  Using fallback pricing (AWS API unavailable)")
        
        if cost_info['total_cost'] > 50:
            click.echo(f"\n   ⚠️  Cost is ${cost_info['total_cost']:.2f}")
    else:
        click.echo(f"\n✅ Using Simulator: FREE (no AWS charges)")
    
    click.echo(f"\n{'=' * 60}")
    click.echo(f"📋 Execution Command:")
    
    if device_arn:
        click.echo(f"\nncrypt generate-key \\")
        click.echo(f"  --bits {bits} \\")
        click.echo(f"  --key-id YOUR_KEY_ID \\")
        click.echo(f"  --backend braket \\")
        click.echo(f"  --device-arn {device_arn}")
    else:
        click.echo(f"\nncrypt generate-key \\")
        click.echo(f"  --bits {bits} \\")
        click.echo(f"  --key-id YOUR_KEY_ID")
    
    click.echo(f"\n{'=' * 60}")


@cli.command()
@click.option('--bits', '-n', default=500, help='Number of circuits to estimate')
@click.option('--device', '-d', 
              type=click.Choice(['ionq', 'rigetti', 'simulator']),
              default='ionq',
              help='Device type (ionq=Forte 36q, rigetti=Ankaa-3 82q)')
@click.option('--profile', '-p', default='default', help='AWS profile for pricing API')
def estimate_cost(bits, device, profile):
    """
    Estimate cost for quantum device usage using real-time AWS pricing.
    
    Supported devices:
    - ionq: IonQ Forte (36 qubits) - https://ionq.com/quantum-systems/forte
    - rigetti: Rigetti Ankaa-3 (82 qubits) - https://qcs.rigetti.com/qpus
    - simulator: Local simulator (free)
    """
    click.echo(f"\n💰 Cost Estimation for {device.upper()}")
    click.echo(f"   Circuits: {bits}")
    click.echo("=" * 50)
    
    if device == 'simulator':
        click.echo("\n✅ Local Simulator: FREE")
        click.echo("   No AWS charges")
        click.echo("   Unlimited usage")
        return
    
    # Get real-time pricing from AWS
    pricer = BraketPricing(aws_profile=profile)
    cost_info = pricer.calculate_cost(bits, device, shots_per_circuit=1)
    
    click.echo(f"\n📊 {cost_info['device']}")
    click.echo(f"   Task cost: ${cost_info['unit_task_cost']} × {bits} = ${cost_info['task_cost']:.2f}")
    click.echo(f"   Shot cost: ${cost_info['unit_shot_cost']} × {bits} = ${cost_info['shot_cost']:.2f}")
    click.echo(f"   {'─' * 40}")
    click.echo(f"   Total: ${cost_info['total_cost']:.2f}")
    
    if cost_info['pricing_source'] == 'AWS Pricing API':
        click.echo(f"\n   📡 Real-time pricing from AWS Pricing API")
    else:
        click.echo(f"\n   ℹ️  Using fallback pricing (updated late 2024)")
        click.echo(f"      AWS Pricing API unavailable - prices may have changed")
    
    total = cost_info['total_cost']
    
    # Warnings
    if total > 100:
        click.echo(f"\n⚠️  HIGH COST: ${total:.2f}")
        click.echo("   Consider reducing circuits or using Rigetti")
    elif total > 50:
        click.echo(f"\n⚠️  Moderate cost: ${total:.2f}")
    else:
        click.echo(f"\n✅ Reasonable cost: ${total:.2f}")
    
    # Comparison with alternative device
    if device == 'ionq':
        rigetti_info = pricer.calculate_cost(bits, 'rigetti', shots_per_circuit=1)
        savings = total - rigetti_info['total_cost']
        if savings > 0:
            click.echo(f"\n💡 Using Rigetti instead would save: ${savings:.2f}")
            click.echo(f"   (Rigetti total: ${rigetti_info['total_cost']:.2f})")
    elif device == 'rigetti':
        click.echo(f"\n💡 Rigetti is the most cost-effective option")
        click.echo(f"   (28x cheaper per shot than IonQ)")


def main():
    """Entry point for CLI."""
    cli(obj={})


if __name__ == '__main__':
    main()

