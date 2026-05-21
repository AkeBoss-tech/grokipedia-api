"""Data models for Grokipedia API responses."""

try:
    from pydantic import BaseModel, Field, ConfigDict
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback to dataclasses
    from dataclasses import dataclass, field

from typing import List, Dict, Optional, Any, Union


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
        model_config = ConfigDict(extra="allow")
        categories: List[str] = Field(default_factory=list)
        lastModified: str = ""
        contentLength: str = ""
        version: str = "1.0"
        lastEditor: str = "system"
        language: str = "en"
        isRedirect: bool = False
        redirectTarget: str = ""
        isWithheld: bool = False
        creationSource: Optional[int] = None
        visibility: Optional[int] = None
    
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
        model_config = ConfigDict(populate_by_name=True, extra="allow")
        results: List[SearchResult]
        totalCount: Optional[int] = None
        searchTimeMs: Optional[float] = None
        facets: List[Dict[str, Any]] = Field(default_factory=list)

        @property
        def total_count(self) -> Optional[int]:
            return self.totalCount

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'SearchResponse':
            return cls(
                results=[SearchResult.from_dict(item) for item in data.get("results", [])],
                totalCount=data.get("totalCount", data.get("total_count")),
                searchTimeMs=data.get("searchTimeMs", data.get("search_time_ms")),
                facets=data.get("facets", []),
            )
    
    class SupportingEvidence(BaseModel):
        """Represents supporting evidence for an edit request."""
        url: Optional[str] = None
        description: Optional[str] = None
    
    class EditRequest(BaseModel):
        """Represents an edit request for a Grokipedia page."""
        model_config = ConfigDict(extra="allow")
        supportingEvidence: Optional[List[SupportingEvidence]] = None
        id: str
        slug: str
        userId: str
        status: str
        type: Union[str, int]
        summary: str = ""
        originalContent: str = ""
        proposedContent: str = ""
        sectionTitle: str = ""
        createdAt: Union[str, int]
        updatedAt: Union[str, int]
        reviewedBy: Optional[str] = None
        reviewedAt: Optional[Union[str, int]] = None
        reviewReason: Optional[str] = None
        upvoteCount: int = 0
        downvoteCount: int = 0
        userVote: Optional[str] = None
        editStartHeader: Optional[str] = None
        editEndHeader: Optional[str] = None
    
    class EditHistoryResponse(BaseModel):
        """Response containing edit history for a page."""
        editRequests: List[EditRequest] = Field(default_factory=list)
        totalCount: int = 0
        hasMore: bool = False

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'EditHistoryResponse':
            return cls(
                editRequests=[EditRequest(**item) for item in data.get("editRequests", [])],
                totalCount=data.get("totalCount", 0),
                hasMore=data.get("hasMore", False),
            )

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
        totalCount: Optional[int] = None
        searchTimeMs: Optional[float] = None
        facets: List[Dict[str, Any]] = field(default_factory=list)

        @property
        def total_count(self) -> Optional[int]:
            return self.totalCount

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'SearchResponse':
            return cls(
                results=[SearchResult.from_dict(item) for item in data.get("results", [])],
                totalCount=data.get("totalCount", data.get("total_count")),
                searchTimeMs=data.get("searchTimeMs", data.get("search_time_ms")),
                facets=data.get("facets", []),
            )
    
    @dataclass
    class SupportingEvidence:
        """Represents supporting evidence for an edit request."""
        url: Optional[str] = None
        description: Optional[str] = None

    @dataclass
    class EditRequest:
        """Represents an edit request for a Grokipedia page."""
        id: str = ""
        slug: str = ""
        user_id: str = ""
        status: str = ""
        type: Union[str, int] = ""
        summary: str = ""
        original_content: str = ""
        proposed_content: str = ""
        section_title: str = ""
        created_at: Union[str, int] = ""
        updated_at: Union[str, int] = ""
        reviewed_by: Optional[str] = None
        reviewed_at: Optional[Union[str, int]] = None
        review_reason: Optional[str] = None
        upvote_count: int = 0
        downvote_count: int = 0
        user_vote: Optional[str] = None
        edit_start_header: Optional[str] = None
        edit_end_header: Optional[str] = None
        supporting_evidence: List['SupportingEvidence'] = field(default_factory=list)
        
        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'EditRequest':
            """Create an EditRequest instance from a dictionary.
            
            Args:
                data: Dictionary containing edit request data
                
            Returns:
                EditRequest instance
            """
            supporting_evidence = [
                SupportingEvidence(**ev) for ev in data.get("supportingEvidence", [])
            ]
            
            return cls(
                supporting_evidence=supporting_evidence,
                id=data.get("id", ""),
                slug=data.get("slug", ""),
                user_id=data.get("userId", ""),
                status=data.get("status", ""),
                type=data.get("type", ""),
                summary=data.get("summary", ""),
                original_content=data.get("originalContent", ""),
                proposed_content=data.get("proposedContent", ""),
                section_title=data.get("sectionTitle", ""),
                created_at=data.get("createdAt", ""),
                updated_at=data.get("updatedAt", ""),
                reviewed_by=data.get("reviewedBy"),
                reviewed_at=data.get("reviewedAt"),
                review_reason=data.get("reviewReason"),
                upvote_count=data.get("upvoteCount", 0),
                downvote_count=data.get("downvoteCount", 0),
                user_vote=data.get("userVote"),
                edit_start_header=data.get("editStartHeader"),
                edit_end_header=data.get("editEndHeader")
            )
    
    @dataclass
    class EditHistoryResponse:
        """Response containing edit history for a page."""
        edit_requests: List['EditRequest'] = field(default_factory=list)
        total_count: int = 0
        has_more: bool = False
        
        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'EditHistoryResponse':
            """Create an EditHistoryResponse instance from a dictionary.
            
            Args:
                data: Dictionary containing edit history response data
                
            Returns:
                EditHistoryResponse instance
            """
            edit_requests = [
                EditRequest.from_dict(er) for er in data.get("editRequests", [])
            ]
            
            return cls(
                edit_requests=edit_requests,
                total_count=data.get("totalCount", 0),
                has_more=data.get("hasMore", False)
            )
