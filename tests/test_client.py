"""Tests for GrokipediaClient."""

import pytest
from unittest.mock import Mock
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


def test_search_normalizes_live_response_shape():
    """Search responses should expose stable aliases for live API keys."""
    client = GrokipediaClient(use_cache=False)

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "results": [{"title": "Python", "slug": "Python", "snippet": "..."}],
        "totalCount": 123,
        "searchTimeMs": 12.5,
        "facets": [],
    }
    client.session.get = Mock(return_value=response)

    results = client.search("Python")
    assert results["totalCount"] == 123
    assert results["total_count"] == 123
    assert results["searchTimeMs"] == 12.5
    assert results["search_time_ms"] == 12.5


def test_get_page_uses_page_preview_endpoint():
    """Page fetches should use the live page-preview endpoint."""
    client = GrokipediaClient(use_cache=False)

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "found": True,
        "page": {"slug": "Python_(programming_language)", "title": "Python", "content": "hello"},
    }
    client.session.get = Mock(return_value=response)

    page = client.get_page("Python_(programming_language)")
    assert page["found"] is True
    called_url = client.session.get.call_args.args[0]
    assert called_url.endswith("/api/page-preview")


def test_typeahead_and_stats_methods():
    """Convenience methods for new live endpoints should work."""
    client = GrokipediaClient(use_cache=False)

    typeahead_response = Mock()
    typeahead_response.raise_for_status.return_value = None
    typeahead_response.json.return_value = {"results": [], "searchTimeMs": 1.2}

    stats_response = Mock()
    stats_response.raise_for_status.return_value = None
    stats_response.json.return_value = {"totalPages": "100"}

    client.session.get = Mock(side_effect=[typeahead_response, stats_response])

    suggestions = client.typeahead("Py")
    stats = client.get_stats()

    assert suggestions["search_time_ms"] == 1.2
    assert stats["totalPages"] == "100"


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
