"""Async client for interacting with Grokipedia API."""

try:
    import aiohttp
    import asyncio
    from copy import deepcopy
    from typing import List, Dict, Optional, Any
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    from .exceptions import (
        GrokipediaError,
        GrokipediaNotFoundError,
        GrokipediaAPIError,
        GrokipediaRateLimitError
    )
    from .version import __version__
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False


if ASYNC_AVAILABLE:
    class AsyncGrokipediaClient:
        """Async client for interacting with Grokipedia API.
        
        This client provides async methods to search and retrieve content from Grokipedia.
        Requires Python 3.7+ and aiohttp.
        
        Attributes:
            base_url (str): Base URL for Grokipedia API
            timeout (int): Request timeout in seconds
            session (aiohttp.ClientSession): HTTP session for making requests
        """
        
        BASE_URL = "https://grokipedia.com"
        SEARCH_ENDPOINT = "/api/full-text-search"
        TYPEAHEAD_ENDPOINT = "/api/typeahead"
        PAGE_ENDPOINT = "/api/page-preview"
        EDIT_REQUESTS_ENDPOINT = "/api/list-edit-requests-by-slug"
        STATS_ENDPOINT = "/api/stats"
        
        def __init__(self, base_url: Optional[str] = None, timeout: int = 60):
            """Initialize the async Grokipedia client.
            
            Args:
                base_url: Optional custom base URL (defaults to grokipedia.com)
                timeout: Request timeout in seconds (default: 60)
            """
            self.base_url = base_url or self.BASE_URL
            self.timeout = aiohttp.ClientTimeout(total=timeout)
            self.session: Optional[aiohttp.ClientSession] = None
        
        async def __aenter__(self):
            """Async context manager entry."""
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'User-Agent': f'grokipedia-api/{__version__}',
                    'Accept': 'application/json'
                }
            )
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            """Async context manager exit."""
            if self.session:
                await self.session.close()
            return False
        
        async def _ensure_session(self):
            """Ensure session is created."""
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=self.timeout,
                    headers={
                        'User-Agent': f'grokipedia-api/{__version__}',
                        'Accept': 'application/json'
                    }
                )
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((GrokipediaError, aiohttp.ClientError)),
            reraise=True
        )
        async def search(
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
            await self._ensure_session()
            url = f"{self.base_url}{self.SEARCH_ENDPOINT}"
            params = {
                "query": query,
                "limit": limit,
                "offset": offset
            }
            
            try:
                async with self.session.get(url, params=params) as response:
                    # Check for rate limiting
                    if response.status == 429:
                        raise GrokipediaRateLimitError("Rate limit exceeded")
                    
                    response.raise_for_status()
                    return self._normalize_search_response(await response.json())
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    raise GrokipediaNotFoundError(f"Search endpoint not found: {e}")
                if e.status == 429:
                    raise GrokipediaRateLimitError("Rate limit exceeded")
                raise GrokipediaAPIError(f"API error during search: {e}")
            except aiohttp.ClientError as e:
                raise GrokipediaError(f"Request error during search: {e}")
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((GrokipediaError, aiohttp.ClientError)),
            reraise=True
        )
        async def get_page(
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
            await self._ensure_session()
            url = f"{self.base_url}{self.PAGE_ENDPOINT}"
            params = {
                "slug": slug,
            }
            
            try:
                async with self.session.get(url, params=params) as response:
                    # Check for rate limiting
                    if response.status == 429:
                        raise GrokipediaRateLimitError("Rate limit exceeded")
                    
                    response.raise_for_status()
                    data = await response.json()
                    
                    if not data.get("found", False):
                        raise GrokipediaNotFoundError(f"Page not found: {slug}")

                    if not include_content:
                        data = deepcopy(data)
                        data.setdefault("page", {})["content"] = ""

                    return data
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    raise GrokipediaNotFoundError(f"Page not found: {slug}")
                if e.status == 429:
                    raise GrokipediaRateLimitError("Rate limit exceeded")
                raise GrokipediaAPIError(f"API error retrieving page: {e}")
            except aiohttp.ClientError as e:
                raise GrokipediaError(f"Request error retrieving page: {e}")
        
        async def search_pages(self, query: str, limit: int = 12) -> List[Dict[str, Any]]:
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
            results = await self.search(query, limit=limit)
            return results.get("results", [])

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((GrokipediaError, aiohttp.ClientError)),
            reraise=True
        )
        async def typeahead(self, query: str) -> Dict[str, Any]:
            """Get typeahead suggestions for a search query."""
            await self._ensure_session()
            url = f"{self.base_url}{self.TYPEAHEAD_ENDPOINT}"

            try:
                async with self.session.get(url, params={"query": query}) as response:
                    if response.status == 429:
                        raise GrokipediaRateLimitError("Rate limit exceeded")

                    response.raise_for_status()
                    return self._normalize_search_response(await response.json())
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    raise GrokipediaNotFoundError(f"Typeahead endpoint not found: {e}")
                if e.status == 429:
                    raise GrokipediaRateLimitError("Rate limit exceeded")
                raise GrokipediaAPIError(f"API error during typeahead: {e}")
            except aiohttp.ClientError as e:
                raise GrokipediaError(f"Request error during typeahead: {e}")

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((GrokipediaError, aiohttp.ClientError)),
            reraise=True
        )
        async def get_stats(self) -> Dict[str, Any]:
            """Get aggregate Grokipedia site statistics."""
            await self._ensure_session()
            url = f"{self.base_url}{self.STATS_ENDPOINT}"

            try:
                async with self.session.get(url) as response:
                    if response.status == 429:
                        raise GrokipediaRateLimitError("Rate limit exceeded")

                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    raise GrokipediaNotFoundError(f"Stats endpoint not found: {e}")
                if e.status == 429:
                    raise GrokipediaRateLimitError("Rate limit exceeded")
                raise GrokipediaAPIError(f"API error retrieving stats: {e}")
            except aiohttp.ClientError as e:
                raise GrokipediaError(f"Request error retrieving stats: {e}")
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((GrokipediaError, aiohttp.ClientError)),
            reraise=True
        )
        async def list_edit_requests_by_slug(
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
            await self._ensure_session()
            url = f"{self.base_url}{self.EDIT_REQUESTS_ENDPOINT}"
            params = {
                "slug": slug,
                "limit": limit,
                "offset": offset
            }
            
            try:
                async with self.session.get(url, params=params) as response:
                    # Check for rate limiting
                    if response.status == 429:
                        raise GrokipediaRateLimitError("Rate limit exceeded")
                    
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    raise GrokipediaNotFoundError(f"Edit requests not found for slug: {slug}")
                if e.status == 429:
                    raise GrokipediaRateLimitError("Rate limit exceeded")
                raise GrokipediaAPIError(f"API error retrieving edit requests: {e}")
            except aiohttp.ClientError as e:
                raise GrokipediaError(f"Request error retrieving edit requests: {e}")
        
        async def close(self):
            """Close the session."""
            if self.session:
                await self.session.close()

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
    
    # Module-level helper functions for concurrent operations
    
    async def search_many(
        queries: List[str],
        limit: int = 12
    ) -> List[Dict[str, Any]]:
        """Search for multiple queries concurrently.
        
        Args:
            queries: List of search query strings
            limit: Maximum number of results per query
        
        Returns:
            List of search result dictionaries
        """
        async with AsyncGrokipediaClient() as client:
            tasks = [client.search(query, limit=limit) for query in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and flatten results
            all_results = []
            for result in results:
                if isinstance(result, dict):
                    all_results.extend(result.get("results", []))
                elif isinstance(result, Exception):
                    # Log error but continue
                    print(f"Error in concurrent search: {result}")
            
            return all_results
    
    async def get_many_pages(
        slugs: List[str],
        include_content: bool = True
    ) -> List[Dict[str, Any]]:
        """Get multiple pages concurrently.
        
        Args:
            slugs: List of page slugs
            include_content: Whether to include full content
        
        Returns:
            List of page dictionaries
        """
        async with AsyncGrokipediaClient() as client:
            tasks = [client.get_page(slug, include_content=include_content) for slug in slugs]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            pages = []
            for result in results:
                if isinstance(result, dict):
                    pages.append(result)
                elif isinstance(result, Exception):
                    # Log error but continue
                    print(f"Error retrieving page: {result}")
            
            return pages

else:
    # Fallback for when aiohttp is not available
    class AsyncGrokipediaClient:
        """Async client requires aiohttp."""
        
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "Async support requires 'aiohttp'. "
                "Install with: pip install grokipedia-api[async]"
            )
