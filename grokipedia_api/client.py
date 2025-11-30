"""Main client for interacting with Grokipedia API."""

import requests
from typing import List, Dict, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .exceptions import GrokipediaError, GrokipediaNotFoundError, GrokipediaAPIError, GrokipediaRateLimitError
from .cache import FileCache


class GrokipediaClient:
    """Client for interacting with Grokipedia API.
    
    This client provides methods to search and retrieve content from Grokipedia.
    
    Attributes:
        base_url (str): Base URL for Grokipedia API
        session (requests.Session): HTTP session for making requests
    """
    
    BASE_URL = "https://grokipedia.com"
    
    def __init__(
        self, 
        base_url: Optional[str] = None, 
        timeout: int = 30,
        use_cache: bool = True,
        cache_ttl: int = 604800  # 7 days in seconds
    ):
        """Initialize the Grokipedia client.
        
        Args:
            base_url: Optional custom base URL (defaults to grokipedia.com)
            timeout: Request timeout in seconds (default: 30)
            use_cache: Whether to use caching (default: True)
            cache_ttl: Cache time-to-live in seconds (default: 7 days)
        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'grokipedia-api/0.1.0',
            'Accept': 'application/json'
        })
        self.use_cache = use_cache
        if use_cache:
            self.cache = FileCache(ttl=cache_ttl)
        else:
            self.cache = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((GrokipediaError, requests.exceptions.RequestException)),
        reraise=True
    )
    def search(
        self,
        query: str,
        limit: int = 12,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search for articles in Grokipedia.
        
        Automatically retries on network errors and rate limits.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return (default: 12)
            offset: Number of results to skip for pagination (default: 0)
        
        Returns:
            Dictionary containing search results with the following keys:
            - results: List of search result dictionaries
            - total_count: Total number of results (if available)
            
        Raises:
            GrokipediaError: If the search request fails
        """
        # Try cache first if enabled
        if self.use_cache and self.cache:
            cache_key = f"search:{query}:{limit}:{offset}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.base_url}/api/full-text-search"
        params = {
            "query": query,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Check for rate limiting
            if response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
                
            result = response.json()
            
            # Cache result if enabled
            if self.use_cache and self.cache:
                cache_key = f"search:{query}:{limit}:{offset}"
                self.cache.set(cache_key, result)
            
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Search endpoint not found: {e}")
            if e.response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
            raise GrokipediaAPIError(f"API error during search: {e}")
        except requests.exceptions.RequestException as e:
            raise GrokipediaError(f"Request error during search: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((GrokipediaError, requests.exceptions.RequestException)),
        reraise=True
    )
    def get_page(
        self,
        slug: str,
        include_content: bool = True,
        validate_links: bool = True
    ) -> Dict[str, Any]:
        """Get a specific page by its slug.
        
        Automatically retries on network errors and rate limits.
        
        Args:
            slug: Page slug (e.g., "United_Petroleum")
            include_content: Whether to include full content (default: True)
            validate_links: Whether to validate links (default: True)
        
        Returns:
            Dictionary containing page data with the following keys:
            - page: Dictionary containing page information including:
                - title: Page title
                - content: Full markdown content
                - citations: List of citation dictionaries
                - images: List of image dictionaries
                - metadata: Page metadata
                - slug: Page slug
            - found: Boolean indicating if the page was found
            
        Raises:
            GrokipediaError: If the request fails
            GrokipediaNotFoundError: If the page is not found
        """
        # Try cache first if enabled
        if self.use_cache and self.cache:
            cache_key = f"page:{slug}:{include_content}:{validate_links}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.base_url}/api/page"
        params = {
            "slug": slug,
            "includeContent": str(include_content).lower(),
            "validateLinks": str(validate_links).lower()
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Check for rate limiting
            if response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
                
            data = response.json()
            
            if not data.get("found", False):
                raise GrokipediaNotFoundError(f"Page not found: {slug}")
            
            # Cache result if enabled
            if self.use_cache and self.cache:
                cache_key = f"page:{slug}:{include_content}:{validate_links}"
                self.cache.set(cache_key, data)
            
            return data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Page not found: {slug}")
            if e.response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
            raise GrokipediaAPIError(f"API error retrieving page: {e}")
        except requests.exceptions.RequestException as e:
            raise GrokipediaError(f"Request error retrieving page: {e}")
    
    def search_pages(self, query: str, limit: int = 12) -> List[Dict[str, Any]]:
        """Search for pages and return results as a list.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return (default: 12)
        
        Returns:
            List of search result dictionaries, each containing:
            - title: Page title
            - slug: Page slug
            - snippet: Content snippet
            - relevanceScore: Relevance score
            - viewCount: Number of views
            
        Raises:
            GrokipediaError: If the search request fails
        """
        results = self.search(query, limit=limit)
        return results.get("results", [])
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((GrokipediaError, requests.exceptions.RequestException)),
        reraise=True
    )
    def list_edit_requests_by_slug(
        self,
        slug: str,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List edit requests for a specific page by its slug.
        
        Automatically retries on network errors and rate limits.
        
        Args:
            slug: Page slug (e.g., "United_States")
            limit: Maximum number of edit requests to return (default: 10)
            offset: Number of results to skip for pagination (default: 0)
        
        Returns:
            Dictionary containing edit history with the following keys:
            - editRequests: List of edit request dictionaries
            - totalCount: Total number of edit requests
            - hasMore: Boolean indicating if there are more results
            
        Raises:
            GrokipediaError: If the request fails
        """
        # Try cache first if enabled
        if self.use_cache and self.cache:
            cache_key = f"edit_requests:{slug}:{limit}:{offset}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.base_url}/api/list-edit-requests-by-slug"
        params = {
            "slug": slug,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Check for rate limiting
            if response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
                
            data = response.json()
            
            # Cache result if enabled
            if self.use_cache and self.cache:
                cache_key = f"edit_requests:{slug}:{limit}:{offset}"
                self.cache.set(cache_key, data)
            
            return data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Edit requests not found for slug: {slug}")
            if e.response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
            raise GrokipediaAPIError(f"API error retrieving edit requests: {e}")
        except requests.exceptions.RequestException as e:
            raise GrokipediaError(f"Request error retrieving edit requests: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close()
        return False
    
    def close(self):
        """Close the session."""
        self.session.close()

