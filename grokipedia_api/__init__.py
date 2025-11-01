"""Grokipedia API - A Python client for accessing Grokipedia content."""

from .client import GrokipediaClient
from .exceptions import (
    GrokipediaError,
    GrokipediaNotFoundError,
    GrokipediaAPIError,
    GrokipediaRateLimitError
)
from .models import (
    Citation,
    Image,
    Page,
    PageMetadata,
    PageStats,
    SearchResult,
    SearchResponse
)
from .export import to_markdown, to_json, to_html, to_plain_text, export_to_file
from .analysis import analyze_page, get_sections, extract_keywords
from .cache import FileCache

try:
    from .async_client import AsyncGrokipediaClient, search_many, get_many_pages
    HAS_ASYNC = True
except ImportError:
    HAS_ASYNC = False

try:
    from .langchain_utils import to_langchain_document, search_to_documents, get_relevant_citations
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

# Base exports
__all__ = [
    "GrokipediaClient",
    "GrokipediaError",
    "GrokipediaNotFoundError",
    "GrokipediaAPIError",
    "GrokipediaRateLimitError",
    "Citation",
    "Image",
    "Page",
    "PageMetadata",
    "PageStats",
    "SearchResult",
    "SearchResponse",
    "to_markdown",
    "to_json",
    "to_html",
    "to_plain_text",
    "export_to_file",
    "analyze_page",
    "get_sections",
    "extract_keywords",
    "FileCache",
]

# Add async exports if available
if HAS_ASYNC:
    __all__.extend(["AsyncGrokipediaClient", "search_many", "get_many_pages"])

# Add langchain exports if available
if HAS_LANGCHAIN:
    __all__.extend(["to_langchain_document", "search_to_documents", "get_relevant_citations"])

__version__ = "0.3.0"

