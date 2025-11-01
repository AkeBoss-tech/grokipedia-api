"""Grokipedia API - A Python client for accessing Grokipedia content."""

from .client import GrokipediaClient
from .exceptions import (
    GrokipediaError,
    GrokipediaNotFoundError,
    GrokipediaAPIError,
    GrokipediaRateLimitError
)

try:
    from .async_client import AsyncGrokipediaClient, search_many, get_many_pages
    __all__ = [
        "GrokipediaClient",
        "AsyncGrokipediaClient",
        "search_many",
        "get_many_pages",
        "GrokipediaError",
        "GrokipediaNotFoundError",
        "GrokipediaAPIError",
        "GrokipediaRateLimitError"
    ]
except ImportError:
    __all__ = [
        "GrokipediaClient",
        "GrokipediaError",
        "GrokipediaNotFoundError",
        "GrokipediaAPIError",
        "GrokipediaRateLimitError"
    ]

__version__ = "0.2.0"

