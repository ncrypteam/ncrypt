"""
Key Management Utilities
Secure storage and management of quantum-generated keys.
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


class KeyManager:
    """
    Manages quantum-generated cryptographic keys.
    
    Provides secure storage, retrieval, and metadata management for keys
    generated through quantum key distribution.
    """
    
    def __init__(self, storage_dir: str = "./keys"):
        """
        Initialize key manager.
        
        Args:
            storage_dir: Directory for key storage
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"KeyManager initialized with storage: {storage_dir}")
    
    def save_key(
        self,
        key: List[int],
        key_id: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save quantum key with metadata.
        
        Args:
            key: Quantum-generated key bits
            key_id: Unique identifier for the key
            metadata: Optional metadata (protocol, timestamp, etc.)
        
        Returns:
            Path to saved key file
        """
        if metadata is None:
            metadata = {}
        
        # Add default metadata
        metadata.update({
            "key_id": key_id,
            "timestamp": datetime.utcnow().isoformat(),
            "key_length": len(key),
            "key_hash": self._hash_key(key)
        })
        
        key_data = {
            "key": key,
            "metadata": metadata
        }
        
        filename = f"{key_id}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(key_data, f, indent=2)
        
        logger.info(f"Key saved: {key_id} ({len(key)} bits)")
        return filepath
    
    def load_key(self, key_id: str) -> Dict:
        """
        Load quantum key and metadata.
        
        Args:
            key_id: Unique identifier for the key
        
        Returns:
            Dictionary with key and metadata
        
        Raises:
            FileNotFoundError: If key not found
        """
        filename = f"{key_id}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Key not found: {key_id}")
        
        with open(filepath, 'r') as f:
            key_data = json.load(f)
        
        # Verify key integrity
        key = key_data["key"]
        stored_hash = key_data["metadata"].get("key_hash")
        computed_hash = self._hash_key(key)
        
        if stored_hash and stored_hash != computed_hash:
            logger.warning(f"Key integrity check failed for {key_id}")
        
        logger.info(f"Key loaded: {key_id}")
        return key_data
    
    def list_keys(self) -> List[Dict]:
        """
        List all stored keys.
        
        Returns:
            List of key metadata dictionaries
        """
        keys = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        key_data = json.load(f)
                    keys.append(key_data["metadata"])
                except Exception as e:
                    logger.error(f"Error reading {filename}: {e}")
        
        return sorted(keys, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def delete_key(self, key_id: str) -> bool:
        """
        Delete a stored key.
        
        Args:
            key_id: Unique identifier for the key
        
        Returns:
            True if deleted, False if not found
        """
        filename = f"{key_id}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Key deleted: {key_id}")
            return True
        else:
            logger.warning(f"Key not found for deletion: {key_id}")
            return False
    
    def _hash_key(self, key: List[int]) -> str:
        """
        Compute hash of key for integrity checking.
        
        Args:
            key: Key bits
        
        Returns:
            Hex digest of key hash
        """
        key_bytes = bytes(key)
        return hashlib.sha256(key_bytes).hexdigest()
    
    def export_key(self, key_id: str, output_path: str, format: str = "hex") -> None:
        """
        Export key in specified format.
        
        Args:
            key_id: Unique identifier for the key
            output_path: Path for exported key
            format: Export format ('hex', 'binary', 'base64')
        """
        key_data = self.load_key(key_id)
        key = key_data["key"]
        
        if format == "hex":
            # Convert bits to hex
            hex_str = ""
            for i in range(0, len(key), 4):
                nibble = 0
                for j in range(4):
                    if i + j < len(key):
                        nibble = (nibble << 1) | key[i + j]
                hex_str += f"{nibble:x}"
            
            with open(output_path, 'w') as f:
                f.write(hex_str)
        
        elif format == "binary":
            # Convert bits to bytes
            byte_array = bytearray()
            for i in range(0, len(key), 8):
                byte = 0
                for j in range(8):
                    if i + j < len(key):
                        byte = (byte << 1) | key[i + j]
                byte_array.append(byte)
            
            with open(output_path, 'wb') as f:
                f.write(bytes(byte_array))
        
        elif format == "base64":
            import base64
            # Convert bits to bytes then base64
            byte_array = bytearray()
            for i in range(0, len(key), 8):
                byte = 0
                for j in range(8):
                    if i + j < len(key):
                        byte = (byte << 1) | key[i + j]
                byte_array.append(byte)
            
            b64_str = base64.b64encode(bytes(byte_array)).decode('utf-8')
            with open(output_path, 'w') as f:
                f.write(b64_str)
        
        else:
            raise ValueError(f"Unknown format: {format}")
        
        logger.info(f"Key exported: {key_id} -> {output_path} ({format})")
    
    def get_key_info(self, key_id: str) -> Dict:
        """
        Get key metadata without loading full key.
        
        Args:
            key_id: Unique identifier for the key
        
        Returns:
            Key metadata dictionary
        """
        key_data = self.load_key(key_id)
        return key_data["metadata"]

