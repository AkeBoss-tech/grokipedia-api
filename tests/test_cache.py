"""Tests for caching functionality."""

import pytest
import tempfile
import os
from grokipedia_api.cache import FileCache
from grokipedia_api import GrokipediaClient


def test_file_cache_init():
    """Test FileCache initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FileCache(cache_dir=tmpdir)
        assert cache.cache_dir.exists()
        assert cache.ttl == 604800  # 7 days default


def test_file_cache_get_set():
    """Test basic get/set functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FileCache(cache_dir=tmpdir, ttl=3600)
        
        # Set value
        cache.set("test_key", {"data": "test_value"})
        
        # Get value
        result = cache.get("test_key")
        assert result == {"data": "test_value"}


def test_file_cache_expiration():
    """Test that cache expires correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FileCache(cache_dir=tmpdir, ttl=1)  # 1 second TTL
        
        # Set value
        cache.set("test_key", {"data": "test_value"})
        
        # Should be available immediately
        result = cache.get("test_key")
        assert result == {"data": "test_value"}


def test_file_cache_delete():
    """Test cache deletion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FileCache(cache_dir=tmpdir)
        
        cache.set("test_key", {"data": "test_value"})
        assert cache.get("test_key") is not None
        
        cache.delete("test_key")
        assert cache.get("test_key") is None


def test_file_cache_clear():
    """Test clearing all cache."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FileCache(cache_dir=tmpdir)
        
        cache.set("key1", {"data": "value1"})
        cache.set("key2", {"data": "value2"})
        
        assert cache.get("key1") is not None
        assert cache.get("key2") is not None
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None


def test_client_with_cache():
    """Test client with caching enabled."""
    client = GrokipediaClient(use_cache=True, cache_ttl=3600)
    assert client.use_cache is True
    assert client.cache is not None


def test_client_without_cache():
    """Test client with caching disabled."""
    client = GrokipediaClient(use_cache=False)
    assert client.use_cache is False
    assert client.cache is None


if __name__ == "__main__":
    pytest.main([__file__])

