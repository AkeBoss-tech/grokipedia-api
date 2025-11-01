"""Tests for export functionality."""

import os
import pytest
import tempfile
from grokipedia_api.export import to_markdown, to_json, to_html, to_plain_text, export_to_file
from grokipedia_api.models import Page, Citation, Image


def test_to_markdown():
    """Test markdown export."""
    page_data = {
        "title": "Test Page",
        "content": "<p>This is test content</p>",
        "description": "A test page",
        "citations": [
            {"title": "Citation 1", "url": "https://example.com", "description": "Desc"}
        ]
    }
    
    md = to_markdown(page_data)
    assert "# Test Page" in md
    assert "A test page" in md
    assert "Citations" in md
    assert "Citation 1" in md


def test_to_json():
    """Test JSON export."""
    page_data = {
        "title": "Test Page",
        "content": "Test content"
    }
    
    json_str = to_json(page_data)
    assert "Test Page" in json_str
    assert "Test content" in json_str
    
    # Should be valid JSON
    import json
    parsed = json.loads(json_str)
    assert parsed["title"] == "Test Page"


def test_to_html():
    """Test HTML export."""
    page_data = {
        "title": "Test Page",
        "content": "Test content"
    }
    
    html = to_html(page_data)
    assert "<!DOCTYPE html>" in html
    assert "<title>Test Page</title>" in html
    assert "Test Page" in html


def test_to_plain_text():
    """Test plain text export."""
    page_data = {
        "title": "Test Page",
        "content": "<p>Test content</p>",
        "description": "A test"
    }
    
    text = to_plain_text(page_data)
    assert "Test Page" in text
    assert "A test" in text
    assert "<p>" not in text  # HTML tags removed


def test_export_to_file():
    """Test exporting to file."""
    page_data = {
        "title": "Test Page",
        "content": "Test content"
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.json")
        export_to_file(page_data, filepath, format="json")
        
        assert os.path.exists(filepath)
        
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
            assert data["title"] == "Test Page"


def test_export_invalid_format():
    """Test invalid export format."""
    page_data = {"title": "Test"}
    
    with pytest.raises(ValueError):
        export_to_file(page_data, "test.xyz", format="invalid")


def test_export_with_pydantic_model():
    """Test export works with Pydantic models."""
    # This will use Pydantic if available, otherwise dataclass
    citation = Citation(
        id="1",
        title="Test Citation",
        description="Description",
        url="https://example.com"
    )
    
    # Should work with either Pydantic or dataclass
    if hasattr(citation, 'model_dump'):
        # Pydantic
        data = citation.model_dump()
    else:
        # Dataclass
        import dataclasses
        data = dataclasses.asdict(citation)
    
    assert "Test Citation" in to_json({"citation": data})


if __name__ == "__main__":
    pytest.main([__file__])

