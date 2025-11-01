"""Data models for Grokipedia API responses."""

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback to dataclasses
    from dataclasses import dataclass, field

from typing import List, Dict, Optional, Any


if PYDANTIC_AVAILABLE:
    # Pydantic models for type safety and validation
    
    class Citation(BaseModel):
        """Represents a citation in a Grokipedia article."""
        id: str
        title: str
        description: str
        url: str
        favicon: str = ""
    
    class Image(BaseModel):
        """Represents an image in a Grokipedia article."""
        id: str
        caption: str
        url: str
        position: str = "CENTER"
        width: int = 0
        height: int = 0
    
    class PageMetadata(BaseModel):
        """Metadata for a Grokipedia page."""
        categories: List[str] = Field(default_factory=list)
        lastModified: str = ""
        contentLength: str = ""
        version: str = "1.0"
        lastEditor: str = "system"
        language: str = "en"
        isRedirect: bool = False
        redirectTarget: str = ""
        isWithheld: bool = False
    
    class PageStats(BaseModel):
        """Statistics for a Grokipedia page."""
        totalViews: str = "0"
        recentViews: str = "0"
        dailyAvgViews: float = 0.0
        qualityScore: float = 0.0
        lastViewed: str = ""
    
    class Page(BaseModel):
        """Represents a full Grokipedia page."""
        slug: str
        title: str
        content: str
        citations: List[Citation] = Field(default_factory=list)
        images: List[Image] = Field(default_factory=list)
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
    
    class SearchResult(BaseModel):
        """Represents a search result."""
        title: str
        slug: str
        snippet: str
        relevanceScore: float = 0.0
        viewCount: str = "0"
        titleHighlights: List[str] = Field(default_factory=list)
        snippetHighlights: List[str] = Field(default_factory=list)
        
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
    
    class SearchResponse(BaseModel):
        """Search response with results."""
        results: List[SearchResult]
        total_count: Optional[int] = None

else:
    # Fallback to dataclasses when Pydantic is not available
    
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
    
    @dataclass
    class SearchResponse:
        """Search response with results."""
        results: List[SearchResult]
        total_count: Optional[int] = None
