"""
AWS Braket Pricing Utilities
Fetches real-time pricing from AWS Pricing API.
"""

import subprocess
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class BraketPricing:
    """Fetch and cache AWS Braket pricing information."""
    
    # Fallback pricing if AWS API fails (as of October 2025)
    FALLBACK_PRICING = {
        'ionq': {'task': 0.30, 'shot': 0.08, 'name': 'IonQ'},
        'rigetti': {'task': 0.30, 'shot': 0.0009, 'name': 'Rigetti'},
        'simulator': {'task': 0.00, 'shot': 0.00, 'name': 'Simulator'}
    }
    
    def __init__(self, aws_profile: str = 'default', region: str = 'us-east-1'):
        """
        Initialize pricing fetcher.
        
        Args:
            aws_profile: AWS CLI profile
            region: AWS region
        """
        self.aws_profile = aws_profile
        self.region = region
        self._pricing_cache = {}
    
    def get_device_pricing(self, device_arn: Optional[str] = None, device_type: Optional[str] = None) -> Dict:
        """
        Get pricing for a specific device.
        
        Args:
            device_arn: Full device ARN
            device_type: Device type ('ionq', 'rigetti', 'simulator')
        
        Returns:
            Dictionary with 'task' and 'shot' costs
        """
        # Determine device type from ARN if provided
        if device_arn:
            if 'ionq' in device_arn.lower():
                device_type = 'ionq'
            elif 'rigetti' in device_arn.lower():
                device_type = 'rigetti'
            elif 'simulator' in device_arn.lower():
                device_type = 'simulator'
        
        if not device_type:
            device_type = 'ionq'  # Default
        
        # Check cache
        if device_type in self._pricing_cache:
            logger.debug(f"Using cached pricing for {device_type}")
            return self._pricing_cache[device_type]
        
        # Try to fetch from AWS
        pricing = self._fetch_from_aws(device_type)
        
        if pricing:
            self._pricing_cache[device_type] = pricing
            return pricing
        
        # Fallback to hardcoded pricing
        logger.warning(f"Using fallback pricing for {device_type}")
        return self.FALLBACK_PRICING.get(device_type, self.FALLBACK_PRICING['ionq'])
    
    def _fetch_from_aws(self, device_type: str) -> Optional[Dict]:
        """
        Fetch pricing from AWS Pricing API.
        
        Args:
            device_type: 'ionq', 'rigetti', or 'simulator'
        
        Returns:
            Pricing dictionary or None if failed
        """
        if device_type == 'simulator':
            return {'task': 0.0, 'shot': 0.0, 'name': 'Local Simulator', 'source': 'free'}
        
        try:
            # Query AWS Pricing API for Braket
            # Note: productFamily filter doesn't work well for Braket, so we filter by service
            cmd = [
                'aws', 'pricing', 'get-products',
                '--service-code', 'AmazonBraket',
                '--format-version', 'aws_v1',
                '--max-results', '100',
                '--region', 'us-east-1',  # Pricing API is only in us-east-1
                '--profile', self.aws_profile
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.warning(f"AWS CLI returned error (code {result.returncode}): {result.stderr.strip()}")
                return None
            
            data = json.loads(result.stdout)
            logger.debug(f"AWS Pricing API returned {len(data.get('PriceList', []))} items")
            
            # Parse pricing data - task and shot pricing are in separate API items
            # Prefer latest generation devices: Forte for IonQ, Ankaa for Rigetti
            preferred_devices = {
                'ionq': ['forte', 'aria'],  # Forte is latest, Aria as fallback
                'rigetti': ['ankaa', 'aspen']  # Ankaa is latest, Aspen as fallback
            }
            
            # Collect all pricing for matching devices
            device_pricing = {}  # device_name -> {'task': X, 'shot': Y}
            
            for price_item in data.get('PriceList', []):
                price_data = json.loads(price_item)
                
                # Check if this is for the right device type
                attributes = price_data.get('product', {}).get('attributes', {})
                # AWS uses 'provider' field for the device vendor (IonQ, Rigetti, etc.)
                provider = attributes.get('provider', '').lower()
                device_name = attributes.get('devicename', '').lower()
                operation = attributes.get('operation', '').lower()
                
                logger.debug(f"Found device in API: provider='{provider}', device='{device_name}', operation='{operation}' (looking for '{device_type}')")
                
                if device_type in provider or device_type in device_name:
                    # Extract pricing from this item
                    terms = price_data.get('terms', {}).get('OnDemand', {})
                    
                    for term_id, term_data in terms.items():
                        price_dimensions = term_data.get('priceDimensions', {})
                        
                        for dim_id, dim_data in price_dimensions.items():
                            unit = dim_data.get('unit', '').lower()
                            price = float(dim_data.get('pricePerUnit', {}).get('USD', 0))
                            
                            # Initialize device entry if not exists
                            if device_name not in device_pricing:
                                device_pricing[device_name] = {'task': None, 'shot': None}
                            
                            # Task pricing is in "Task" operation
                            if 'quantum-task' in unit and operation == 'task':
                                device_pricing[device_name]['task'] = price
                                logger.debug(f"Found task price for {device_name}: ${price}")
                            # Shot pricing is in "CompleteTask" operation
                            elif 'quantum-shot' in unit and operation == 'completetask':
                                device_pricing[device_name]['shot'] = price
                                logger.debug(f"Found shot price for {device_name}: ${price}")
            
            # Select the best device based on preference
            selected_device = None
            for preferred in preferred_devices.get(device_type, []):
                for dev_name in device_pricing:
                    if preferred in dev_name:
                        if device_pricing[dev_name]['task'] is not None and device_pricing[dev_name]['shot'] is not None:
                            selected_device = dev_name
                            break
                if selected_device:
                    break
            
            # If no preferred device found, pick any complete one
            if not selected_device:
                for dev_name, pricing in device_pricing.items():
                    if pricing['task'] is not None and pricing['shot'] is not None:
                        selected_device = dev_name
                        break
            
            # Return pricing for selected device
            if selected_device:
                pricing = device_pricing[selected_device]
                device_name_pretty = 'IonQ' if device_type == 'ionq' else 'Rigetti'
                logger.debug(f"Selected device: {selected_device}")
                return {
                    'task': pricing['task'],
                    'shot': pricing['shot'],
                    'name': device_name_pretty,
                    'source': 'AWS Pricing API'
                }
            
            # If no complete pricing found, log what we found
            if device_pricing:
                logger.warning(f"Found {len(device_pricing)} {device_type} devices but none with complete pricing")
            else:
                logger.warning(f"No pricing found in AWS API for {device_type} after checking {len(data.get('PriceList', []))} items")
            return None
            
        except subprocess.TimeoutExpired:
            logger.warning("AWS Pricing API timeout")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AWS API response: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error fetching AWS pricing: {e}")
            return None
    
    def get_all_pricing(self) -> Dict:
        """
        Get pricing for all device types.
        
        Returns:
            Dictionary of device_type -> pricing
        """
        return {
            'ionq': self.get_device_pricing(device_type='ionq'),
            'rigetti': self.get_device_pricing(device_type='rigetti'),
            'simulator': self.get_device_pricing(device_type='simulator')
        }
    
    def calculate_cost(
        self,
        n_circuits: int,
        device_type: str,
        shots_per_circuit: int = 1
    ) -> Dict:
        """
        Calculate total cost for an operation.
        
        Args:
            n_circuits: Number of circuits to run
            device_type: 'ionq', 'rigetti', or 'simulator'
            shots_per_circuit: Shots per circuit (default: 1)
        
        Returns:
            Cost breakdown dictionary
        """
        pricing = self.get_device_pricing(device_type=device_type)
        
        task_cost = pricing['task'] * n_circuits
        shot_cost = pricing['shot'] * n_circuits * shots_per_circuit
        total = task_cost + shot_cost
        
        return {
            'device': pricing['name'],
            'device_type': device_type,
            'circuits': n_circuits,
            'shots_per_circuit': shots_per_circuit,
            'task_cost': task_cost,
            'shot_cost': shot_cost,
            'total_cost': total,
            'unit_task_cost': pricing['task'],
            'unit_shot_cost': pricing['shot'],
            'pricing_source': pricing.get('source', 'fallback')
        }

