"""Tests for data models."""

import pytest
from grokipedia_api.models import Page, Citation, Image, SearchResult, PageMetadata, PageStats


def test_search_result_from_dict():
    """Test SearchResult.from_dict()."""
    data = {
        "title": "Test Title",
        "slug": "Test_Title",
        "snippet": "This is a test snippet",
        "relevanceScore": 100.5,
        "viewCount": "1234",
        "titleHighlights": ["Test"],
        "snippetHighlights": ["test"]
    }
    
    result = SearchResult.from_dict(data)
    assert result.title == "Test Title"
    assert result.slug == "Test_Title"
    assert result.snippet == "This is a test snippet"
    assert result.relevanceScore == 100.5
    assert result.viewCount == "1234"


def test_citation_creation():
    """Test Citation creation."""
    citation = Citation(
        id="1",
        title="Test Citation",
        description="Test description",
        url="https://example.com",
        favicon="favicon.ico"
    )
    
    assert citation.id == "1"
    assert citation.title == "Test Citation"
    assert citation.url == "https://example.com"


def test_image_creation():
    """Test Image creation."""
    image = Image(
        id="img1",
        caption="Test Image",
        url="https://example.com/image.jpg",
        position="CENTER",
        width=800,
        height=600
    )
    
    assert image.id == "img1"
    assert image.caption == "Test Image"
    assert image.width == 800
    assert image.height == 600


def test_page_from_dict():
    """Test Page.from_dict()."""
    data = {
        "page": {
            "slug": "Test_Page",
            "title": "Test Page",
            "content": "Test content here",
            "citations": [
                {
                    "id": "1",
                    "title": "Citation 1",
                    "description": "Description 1",
                    "url": "https://example.com/1"
                }
            ],
            "images": [
                {
                    "id": "img1",
                    "caption": "Test Image",
                    "url": "https://example.com/img.jpg",
                    "position": "CENTER",
                    "width": 800,
                    "height": 600
                }
            ],
            "metadata": {
                "categories": ["Technology"],
                "lastModified": "1234567890",
                "contentLength": "500",
                "version": "1.0",
                "lastEditor": "test",
                "language": "en"
            },
            "stats": {
                "totalViews": "1000",
                "recentViews": "500",
                "dailyAvgViews": 50.0,
                "qualityScore": 0.95,
                "lastViewed": "1234567890"
            }
        }
    }
    
    page = Page.from_dict(data)
    assert page.slug == "Test_Page"
    assert page.title == "Test Page"
    assert len(page.citations) == 1
    assert len(page.images) == 1
    assert page.metadata is not None
    assert page.stats is not None


if __name__ == "__main__":
    pytest.main([__file__])

