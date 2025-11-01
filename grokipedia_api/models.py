"""Data models for Grokipedia API responses."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class Citation:
    """Represents a citation in a Grokipedia article."""
    id: str
    title: str
    description: str
    url: str
    favicon: str = ""


@dataclass
class Image:
    """Represents an image in a Grokipedia article."""
    id: str
    caption: str
    url: str
    position: str = "CENTER"
    width: int = 0
    height: int = 0


@dataclass
class PageMetadata:
    """Metadata for a Grokipedia page."""
    categories: List[str] = field(default_factory=list)
    lastModified: str = ""
    contentLength: str = ""
    version: str = "1.0"
    lastEditor: str = "system"
    language: str = "en"
    isRedirect: bool = False
    redirectTarget: str = ""
    isWithheld: bool = False


@dataclass
class PageStats:
    """Statistics for a Grokipedia page."""
    totalViews: str = "0"
    recentViews: str = "0"
    dailyAvgViews: float = 0.0
    qualityScore: float = 0.0
    lastViewed: str = ""


@dataclass
class Page:
    """Represents a full Grokipedia page."""
    slug: str
    title: str
    content: str
    citations: List[Citation] = field(default_factory=list)
    images: List[Image] = field(default_factory=list)
    metadata: Optional[PageMetadata] = None
    stats: Optional[PageStats] = None
    description: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Page':
        """Create a Page instance from a dictionary.
        
        Args:
            data: Dictionary containing page data
            
        Returns:
            Page instance
        """
        page_data = data.get("page", {})
        
        citations = [
            Citation(**citation) for citation in page_data.get("citations", [])
        ]
        
        images = [
            Image(**image) for image in page_data.get("images", [])
        ]
        
        metadata = None
        if "metadata" in page_data:
            metadata = PageMetadata(**page_data["metadata"])
        
        stats = None
        if "stats" in page_data:
            stats = PageStats(**page_data["stats"])
        
        return cls(
            slug=page_data.get("slug", ""),
            title=page_data.get("title", ""),
            content=page_data.get("content", ""),
            citations=citations,
            images=images,
            metadata=metadata,
            stats=stats,
            description=page_data.get("description", "")
        )


@dataclass
class SearchResult:
    """Represents a search result."""
    title: str
    slug: str
    snippet: str
    relevanceScore: float = 0.0
    viewCount: str = "0"
    titleHighlights: List[str] = field(default_factory=list)
    snippetHighlights: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """Create a SearchResult instance from a dictionary.
        
        Args:
            data: Dictionary containing search result data
            
        Returns:
            SearchResult instance
        """
        return cls(
            title=data.get("title", ""),
            slug=data.get("slug", ""),
            snippet=data.get("snippet", ""),
            relevanceScore=data.get("relevanceScore", 0.0),
            viewCount=data.get("viewCount", "0"),
            titleHighlights=data.get("titleHighlights", []),
            snippetHighlights=data.get("snippetHighlights", [])
        )

