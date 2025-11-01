"""Main client for interacting with Grokipedia API."""

import requests
from typing import List, Dict, Optional, Any
from .exceptions import GrokipediaError, GrokipediaNotFoundError, GrokipediaAPIError


class GrokipediaClient:
    """Client for interacting with Grokipedia API.
    
    This client provides methods to search and retrieve content from Grokipedia.
    
    Attributes:
        base_url (str): Base URL for Grokipedia API
        session (requests.Session): HTTP session for making requests
    """
    
    BASE_URL = "https://grokipedia.com"
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """Initialize the Grokipedia client.
        
        Args:
            base_url: Optional custom base URL (defaults to grokipedia.com)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'grokipedia-api/0.1.0',
            'Accept': 'application/json'
        })
    
    def search(
        self,
        query: str,
        limit: int = 12,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search for articles in Grokipedia.
        
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
        url = f"{self.base_url}/api/full-text-search"
        params = {
            "query": query,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Search endpoint not found: {e}")
            raise GrokipediaAPIError(f"API error during search: {e}")
        except requests.exceptions.RequestException as e:
            raise GrokipediaError(f"Request error during search: {e}")
    
    def get_page(
        self,
        slug: str,
        include_content: bool = True,
        validate_links: bool = True
    ) -> Dict[str, Any]:
        """Get a specific page by its slug.
        
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
        url = f"{self.base_url}/api/page"
        params = {
            "slug": slug,
            "includeContent": str(include_content).lower(),
            "validateLinks": str(validate_links).lower()
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("found", False):
                raise GrokipediaNotFoundError(f"Page not found: {slug}")
            
            return data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise GrokipediaNotFoundError(f"Page not found: {slug}")
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

