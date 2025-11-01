"""Caching utilities for Grokipedia API."""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


class FileCache:
    """Simple file-based cache with TTL (Time To Live).
    
    Default TTL is 7 days (604800 seconds).
    """
    
    def __init__(self, cache_dir: Optional[str] = None, ttl: int = 604800):
        """Initialize file cache.
        
        Args:
            cache_dir: Directory for cache files (default: ~/.grokipedia_cache)
            ttl: Time to live in seconds (default: 7 days = 604800s)
        """
        if cache_dir is None:
            cache_dir = os.path.join(Path.home(), ".grokipedia_cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key."""
        # Sanitize key for filename
        safe_key = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in key)
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check if expired
            if time.time() - data['timestamp'] > self.ttl:
                # Cache expired, delete file
                cache_path.unlink()
                return None
            
            return data['value']
        
        except (json.JSONDecodeError, KeyError, IOError):
            # Invalid cache file, delete it
            if cache_path.exists():
                cache_path.unlink()
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        """
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                'timestamp': time.time(),
                'value': value
            }
            
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        except (TypeError, IOError) as e:
            # Value not serializable or write failed
            print(f"Warning: Failed to cache value: {e}")
    
    def clear(self) -> None:
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    def delete(self, key: str) -> None:
        """Delete specific cache entry.
        
        Args:
            key: Cache key to delete
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    def get_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cache entry info (timestamps, age, etc.).
        
        Args:
            key: Cache key
            
        Returns:
            Dictionary with cache info or None
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            timestamp = data['timestamp']
            age_seconds = time.time() - timestamp
            expires_in = self.ttl - age_seconds
            
            return {
                'key': key,
                'timestamp': timestamp,
                'created': datetime.fromtimestamp(timestamp).isoformat(),
                'age_seconds': age_seconds,
                'age_hours': age_seconds / 3600,
                'age_days': age_seconds / 86400,
                'expires_in': expires_in,
                'expired': expires_in <= 0,
                'file_size': cache_path.stat().st_size
            }
        
        except (json.JSONDecodeError, KeyError, IOError):
            return None

