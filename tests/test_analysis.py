"""Tests for analysis functionality."""

import pytest
from grokipedia_api.analysis import analyze_page, get_sections, extract_keywords


def test_analyze_page_basic():
    """Test basic page analysis."""
    page_data = {
        "title": "Test Page",
        "content": "This is a test page with some content. It has multiple sentences. Here's another one."
    }
    
    analysis = analyze_page(page_data)
    
    assert "title" in analysis
    assert "word_count" in analysis
    assert "character_count" in analysis
    assert "sentence_count" in analysis
    assert "reading_time_minutes" in analysis
    assert "complexity_score" in analysis
    
    assert analysis["title"] == "Test Page"
    assert analysis["word_count"] > 0


def test_analyze_page_with_sections():
    """Test analysis of page with headings."""
    page_data = {
        "title": "Test Page",
        "content": "# Section 1\n\nThis is section one.\n\n## Subsection\n\nMore content here."
    }
    
    analysis = analyze_page(page_data)
    
    assert analysis["heading_count"] >= 1
    assert analysis["word_count"] > 0


def test_get_sections():
    """Test section extraction."""
    page_data = {
        "title": "Test Page",
        "content": "# Section 1\nContent for section 1\n\n## Subsection\nSubsection content\n\n# Section 2\nContent for section 2"
    }
    
    sections = get_sections(page_data)
    
    assert len(sections) >= 2
    assert any(s["title"] == "Section 1" for s in sections)
    assert any(s["title"] == "Section 2" for s in sections)


def test_extract_keywords():
    """Test keyword extraction."""
    page_data = {
        "title": "Python Programming",
        "content": "Python is a programming language. Python is versatile. Programming with Python is fun. Language development continues."
    }
    
    keywords = extract_keywords(page_data, top_n=5)
    
    assert len(keywords) <= 5
    assert all("word" in kw and "count" in kw for kw in keywords)
    
    # "python" should be a top keyword
    words = [kw["word"] for kw in keywords]
    assert "python" in words


def test_complexity_levels():
    """Test that complexity levels are assigned correctly."""
    from grokipedia_api.analysis import _get_complexity_level
    
    assert _get_complexity_level(2.0) == "Very Easy"
    assert _get_complexity_level(4.5) == "Easy"
    assert _get_complexity_level(6.0) == "Medium"
    assert _get_complexity_level(8.0) == "Hard"
    assert _get_complexity_level(9.5) == "Very Hard"


if __name__ == "__main__":
    pytest.main([__file__])

