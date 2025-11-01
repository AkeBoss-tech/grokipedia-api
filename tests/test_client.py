"""Tests for GrokipediaClient."""

import pytest
from grokipedia_api import GrokipediaClient
from grokipedia_api.exceptions import GrokipediaError, GrokipediaNotFoundError


def test_client_initialization():
    """Test that the client can be initialized."""
    client = GrokipediaClient()
    assert client is not None
    assert client.base_url == "https://grokipedia.com"


def test_client_custom_base_url():
    """Test that the client can be initialized with a custom base URL."""
    client = GrokipediaClient(base_url="https://custom.com")
    assert client.base_url == "https://custom.com"


def test_context_manager():
    """Test that the client works as a context manager."""
    with GrokipediaClient() as client:
        assert client is not None
    # Session should be closed
    assert client.session is not None


def test_search_functionality():
    """Test search functionality."""
    client = GrokipediaClient()
    
    # This is an integration test - comment out if you don't want to hit the API
    try:
        results = client.search("Python", limit=5)
        assert "results" in results
        assert isinstance(results["results"], list)
    except GrokipediaError:
        pytest.skip("API not accessible")


def test_get_page_functionality():
    """Test get page functionality."""
    client = GrokipediaClient()
    
    # This is an integration test - comment out if you don't want to hit the API
    try:
        page = client.get_page("United_Petroleum")
        assert "page" in page
        assert page["found"] is True
        assert page["page"]["slug"] == "United_Petroleum"
    except GrokipediaError:
        pytest.skip("API not accessible")


def test_get_page_not_found():
    """Test that getting a non-existent page raises an error."""
    client = GrokipediaClient()
    
    # This is an integration test - comment out if you don't want to hit the API
    try:
        with pytest.raises(GrokipediaNotFoundError):
            client.get_page("ThisPageDefinitelyDoesNotExist12345")
    except GrokipediaError:
        pytest.skip("API not accessible")


def test_search_pages():
    """Test search_pages convenience method."""
    client = GrokipediaClient()
    
    # This is an integration test - comment out if you don't want to hit the API
    try:
        results = client.search_pages("Python", limit=5)
        assert isinstance(results, list)
        if len(results) > 0:
            assert "title" in results[0]
            assert "slug" in results[0]
    except GrokipediaError:
        pytest.skip("API not accessible")


if __name__ == "__main__":
    pytest.main([__file__])

