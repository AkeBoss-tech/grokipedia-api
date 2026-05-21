"""Main client for interacting with Grokipedia API."""

from copy import deepcopy
import requests
from typing import List, Dict, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .exceptions import GrokipediaError, GrokipediaNotFoundError, GrokipediaAPIError, GrokipediaRateLimitError
from .cache import FileCache
from .version import __version__


class GrokipediaClient:
    """Client for interacting with Grokipedia API.
    
    This client provides methods to search and retrieve content from Grokipedia.
    
    Attributes:
        base_url (str): Base URL for Grokipedia API
        session (requests.Session): HTTP session for making requests
    """
    
    BASE_URL = "https://grokipedia.com"
    SEARCH_ENDPOINT = "/api/full-text-search"
    TYPEAHEAD_ENDPOINT = "/api/typeahead"
    PAGE_ENDPOINT = "/api/page-preview"
    EDIT_REQUESTS_ENDPOINT = "/api/list-edit-requests-by-slug"
    STATS_ENDPOINT = "/api/stats"
    
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
            'User-Agent': f'grokipedia-api/{__version__}',
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
            - totalCount: Total number of results from the live API
            - total_count: Stable alias for totalCount
            
        Raises:
            GrokipediaError: If the search request fails
        """
        # Try cache first if enabled
        if self.use_cache and self.cache:
            cache_key = f"search:{query}:{limit}:{offset}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.base_url}{self.SEARCH_ENDPOINT}"
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
                
            result = self._normalize_search_response(response.json())
            
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
            slug: Page slug (e.g., "Python_(programming_language)")
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
        
        url = f"{self.base_url}{self.PAGE_ENDPOINT}"
        params = {
            "slug": slug,
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

            if not include_content:
                data = deepcopy(data)
                data.setdefault("page", {})["content"] = ""
            
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((GrokipediaError, requests.exceptions.RequestException)),
        reraise=True
    )
    def typeahead(self, query: str) -> Dict[str, Any]:
        """Get typeahead suggestions for a search query."""
        if self.use_cache and self.cache:
            cache_key = f"typeahead:{query}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        url = f"{self.base_url}{self.TYPEAHEAD_ENDPOINT}"
        params = {"query": query}

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            result = self._normalize_search_response(response.json())

            if self.use_cache and self.cache:
                self.cache.set(cache_key, result)

            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Typeahead endpoint not found: {e}")
            if e.response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
            raise GrokipediaAPIError(f"API error during typeahead: {e}")
        except requests.exceptions.RequestException as e:
            raise GrokipediaError(f"Request error during typeahead: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((GrokipediaError, requests.exceptions.RequestException)),
        reraise=True
    )
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate Grokipedia site statistics."""
        if self.use_cache and self.cache:
            cache_key = "stats"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        url = f"{self.base_url}{self.STATS_ENDPOINT}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()

            if self.use_cache and self.cache:
                self.cache.set(cache_key, result)

            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Stats endpoint not found: {e}")
            if e.response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
            raise GrokipediaAPIError(f"API error retrieving stats: {e}")
        except requests.exceptions.RequestException as e:
            raise GrokipediaError(f"Request error retrieving stats: {e}")
    
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
    def typeahead(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get typeahead/autocomplete suggestions for search.
        
        Automatically retries on network errors and rate limits.
        
        Args:
            query: Search query string for suggestions
            limit: Maximum number of suggestions to return (default: 5)
        
        Returns:
            Dictionary containing typeahead suggestions
            
        Raises:
            GrokipediaError: If the request fails
        """
        # Try cache first if enabled
        if self.use_cache and self.cache:
            cache_key = f"typeahead:{query}:{limit}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.base_url}/api/typeahead"
        params = {
            "query": query,
            "limit": limit
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
                cache_key = f"typeahead:{query}:{limit}"
                self.cache.set(cache_key, result)
            
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Typeahead endpoint not found: {e}")
            if e.response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
            raise GrokipediaAPIError(f"API error during typeahead: {e}")
        except requests.exceptions.RequestException as e:
            raise GrokipediaError(f"Request error during typeahead: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((GrokipediaError, requests.exceptions.RequestException)),
        reraise=True
    )
    def get_constants(self) -> Dict[str, Any]:
        """Get application constants and configuration.
        
        Automatically retries on network errors and rate limits.
        
        Returns:
            Dictionary containing application constants
            
        Raises:
            GrokipediaError: If the request fails
        """
        # Try cache first if enabled
        if self.use_cache and self.cache:
            cache_key = "constants"
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.base_url}/api/constants"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Check for rate limiting
            if response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
                
            result = response.json()
            
            # Cache result if enabled
            if self.use_cache and self.cache:
                cache_key = "constants"
                self.cache.set(cache_key, result)
            
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Constants endpoint not found: {e}")
            if e.response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
            raise GrokipediaAPIError(f"API error retrieving constants: {e}")
        except requests.exceptions.RequestException as e:
            raise GrokipediaError(f"Request error retrieving constants: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((GrokipediaError, requests.exceptions.RequestException)),
        reraise=True
    )
    def list_edit_requests(
        self,
        limit: int = 20,
        status: Optional[List[str]] = None,
        exclude_user_id: Optional[List[str]] = None,
        include_counts: bool = True
    ) -> Dict[str, Any]:
        """List all edit requests with optional filtering.
        
        Automatically retries on network errors and rate limits.
        
        Args:
            limit: Maximum number of edit requests to return (default: 20)
            status: List of statuses to filter by (e.g., ["EDIT_REQUEST_STATUS_APPROVED"])
            exclude_user_id: List of user IDs to exclude from results
            include_counts: Whether to include count information (default: True)
        
        Returns:
            Dictionary containing edit requests and metadata
            
        Raises:
            GrokipediaError: If the request fails
        """
        # Try cache first if enabled
        cache_key = f"edit_requests:{limit}:{status}:{exclude_user_id}:{include_counts}"
        if self.use_cache and self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        url = f"{self.base_url}/api/list-edit-requests"
        params = {
            "limit": limit,
            "includeCounts": str(include_counts).lower()
        }
        
        if status:
            params["status"] = status
        if exclude_user_id:
            params["excludeUserId"] = exclude_user_id
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Check for rate limiting
            if response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
                
            data = response.json()
            
            # Cache result if enabled
            if self.use_cache and self.cache:
                self.cache.set(cache_key, data)
            
            return data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Edit requests endpoint not found: {e}")
            if e.response.status_code == 429:
                raise GrokipediaRateLimitError("Rate limit exceeded")
            raise GrokipediaAPIError(f"API error retrieving edit requests: {e}")
        except requests.exceptions.RequestException as e:
            raise GrokipediaError(f"Request error retrieving edit requests: {e}")
    
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
        
        url = f"{self.base_url}{self.EDIT_REQUESTS_ENDPOINT}"
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

    @staticmethod
    def _normalize_search_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Add stable aliases for evolving search response shapes."""
        normalized = dict(data)
        if "total_count" not in normalized and "totalCount" in normalized:
            normalized["total_count"] = normalized["totalCount"]
        if "search_time_ms" not in normalized and "searchTimeMs" in normalized:
            normalized["search_time_ms"] = normalized["searchTimeMs"]
        normalized.setdefault("facets", [])
        return normalized
