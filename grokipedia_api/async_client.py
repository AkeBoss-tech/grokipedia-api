"""Async client for interacting with Grokipedia API."""

try:
    import aiohttp
    import asyncio
    from typing import List, Dict, Optional, Any
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    from .exceptions import (
        GrokipediaError,
        GrokipediaNotFoundError,
        GrokipediaAPIError,
        GrokipediaRateLimitError
    )
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
                    'User-Agent': 'grokipedia-api/0.1.1',
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
                        'User-Agent': 'grokipedia-api/0.1.1',
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
                - total_count: Total number of results (if available)
                
            Raises:
                GrokipediaError: If the search request fails
            """
            await self._ensure_session()
            url = f"{self.base_url}/api/full-text-search"
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
                    return await response.json()
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
            await self._ensure_session()
            url = f"{self.base_url}/api/page"
            params = {
                "slug": slug,
                "includeContent": str(include_content).lower(),
                "validateLinks": str(validate_links).lower()
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
        
        async def close(self):
            """Close the session."""
            if self.session:
                await self.session.close()
    
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

