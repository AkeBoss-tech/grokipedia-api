"""Custom exceptions for Grokipedia API."""


class GrokipediaError(Exception):
    """Base exception for Grokipedia API errors."""
    pass


class GrokipediaNotFoundError(GrokipediaError):
    """Exception raised when a requested resource is not found."""
    pass


class GrokipediaAPIError(GrokipediaError):
    """Exception raised when there's an API-related error."""
    pass


class GrokipediaRateLimitError(GrokipediaError):
    """Exception raised when rate limit is exceeded."""
    pass

