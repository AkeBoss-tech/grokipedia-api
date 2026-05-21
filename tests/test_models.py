"""Tests for data models."""

import pytest
from grokipedia_api.models import Page, Citation, Image, SearchResult, SearchResponse, EditHistoryResponse


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


def test_search_response_from_live_shape():
    """SearchResponse should understand live Grokipedia keys."""
    response = SearchResponse.from_dict({
        "results": [{"title": "Python", "slug": "Python", "snippet": "..."}],
        "totalCount": 42,
        "searchTimeMs": 4.2,
        "facets": [],
    })

    assert response.totalCount == 42
    assert response.total_count == 42
    assert response.searchTimeMs == 4.2


def test_edit_history_response_from_live_shape():
    """Edit history parsing should tolerate missing optional fields and int timestamps."""
    history = EditHistoryResponse.from_dict({
        "editRequests": [{
            "id": "1",
            "slug": "Python_(programming_language)",
            "userId": "user-1",
            "status": "APPROVED",
            "type": 1,
            "summary": "summary",
            "originalContent": "",
            "proposedContent": "",
            "sectionTitle": "",
            "createdAt": 1774552725,
            "updatedAt": 1774552818,
            "upvoteCount": 0,
            "downvoteCount": 0,
        }],
        "totalCount": 1,
        "hasMore": False,
    })

    assert history.totalCount == 1
    assert history.editRequests[0].slug == "Python_(programming_language)"


if __name__ == "__main__":
    pytest.main([__file__])
