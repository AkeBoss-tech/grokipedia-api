"""Content analysis utilities for Grokipedia pages."""

import re
from typing import Any, Dict, List, Optional, Union


def analyze_page(page: Union[Dict[str, Any], 'Page']) -> Dict[str, Any]:
    """Analyze page content and return statistics.
    
    Args:
        page: Page data (dict or Page model)
        
    Returns:
        Dictionary with analysis results
    """
    # Handle both dict and model
    if hasattr(page, 'model_dump'):
        # Pydantic model
        data = page.model_dump()
    else:
        # Dictionary
        data = page if isinstance(page, dict) else {}
    
    content = data.get('content', '')
    title = data.get('title', '')
    citations = data.get('citations', [])
    
    # Remove HTML tags for word count
    clean_content = re.sub(r'<[^>]+>', '', content)
    
    # Basic stats
    words = len(clean_content.split())
    characters = len(clean_content)
    paragraphs = len([p for p in clean_content.split('\n\n') if p.strip()])
    
    # Sentences (simple count by periods)
    sentences = len([s for s in re.split(r'[.!?]', clean_content) if s.strip()])
    
    # Reading time estimate (average 200 words per minute)
    reading_time_minutes = words / 200 if words > 0 else 0
    
    # Heading count
    headings = len(re.findall(r'^#+\s', content, re.MULTILINE))
    
    # Link count
    links = len(re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content))
    
    # Citation count
    citation_count = len(citations) if isinstance(citations, list) else 0
    
    # Estimate complexity (simple metric based on word length and sentence length)
    avg_word_length = sum(len(word) for word in clean_content.split()) / words if words > 0 else 0
    avg_sentence_length = words / sentences if sentences > 0 else 0
    complexity_score = min(10, (avg_word_length - 3) * 0.5 + (avg_sentence_length / 20))
    
    return {
        'title': title,
        'word_count': words,
        'character_count': characters,
        'paragraph_count': paragraphs,
        'sentence_count': sentences,
        'reading_time_minutes': round(reading_time_minutes, 1),
        'reading_time_readable': f"{int(reading_time_minutes)}m {int((reading_time_minutes % 1) * 60)}s",
        'heading_count': headings,
        'link_count': links,
        'citation_count': citation_count,
        'avg_word_length': round(avg_word_length, 2),
        'avg_sentence_length': round(avg_sentence_length, 2),
        'complexity_score': round(complexity_score, 2),
        'complexity_level': _get_complexity_level(complexity_score)
    }


def _get_complexity_level(score: float) -> str:
    """Get human-readable complexity level."""
    if score < 3:
        return "Very Easy"
    elif score < 5:
        return "Easy"
    elif score < 7:
        return "Medium"
    elif score < 8.5:
        return "Hard"
    else:
        return "Very Hard"


def get_sections(page: Union[Dict[str, Any], 'Page']) -> List[Dict[str, str]]:
    """Extract sections from page content.
    
    Args:
        page: Page data (dict or Page model)
        
    Returns:
        List of section dictionaries with title and content
    """
    # Handle both dict and model
    if hasattr(page, 'model_dump'):
        # Pydantic model
        content = page.model_dump().get('content', '')
    else:
        # Dictionary
        content = page.get('content', '') if isinstance(page, dict) else ''
    
    sections = []
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        # Check if it's a heading
        if line.startswith('#'):
            # Save previous section
            if current_section is not None:
                sections.append({
                    'title': current_section,
                    'content': '\n'.join(current_content).strip()
                })
            
            # Start new section
            current_section = line.lstrip('#').strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_section is not None:
        sections.append({
            'title': current_section,
            'content': '\n'.join(current_content).strip()
        })
    
    return sections


def extract_keywords(page: Union[Dict[str, Any], 'Page'], top_n: int = 10) -> List[Dict[str, Any]]:
    """Extract top keywords from page content.
    
    Args:
        page: Page data (dict or Page model)
        top_n: Number of top keywords to return
        
    Returns:
        List of keyword dictionaries with word and count
    """
    # Handle both dict and model
    if hasattr(page, 'model_dump'):
        # Pydantic model
        content = page.model_dump().get('content', '')
    else:
        # Dictionary
        content = page.get('content', '') if isinstance(page, dict) else ''
    
    # Remove HTML tags
    clean_content = re.sub(r'<[^>]+>', '', content)
    
    # Simple stop words list
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'it', 'its', 'they', 'them', 'their', 'there'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]{4,}\b', clean_content.lower())
    
    # Count frequencies
    word_counts = {}
    for word in words:
        if word not in stop_words:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Return top N
    return [
        {'word': word, 'count': count}
        for word, count in sorted_words[:top_n]
    ]

