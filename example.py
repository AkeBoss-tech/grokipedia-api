#!/usr/bin/env python3
"""
Example script demonstrating the Grokipedia API usage.
"""

from grokipedia_api import GrokipediaClient
from grokipedia_api.exceptions import GrokipediaNotFoundError


def main():
    """Main example function."""
    # Initialize the client
    print("Initializing Grokipedia client...")
    client = GrokipediaClient()
    
    # Example 1: Search for articles
    print("\n1. Searching for 'artificial intelligence' articles...")
    try:
        results = client.search("artificial intelligence", limit=5)
        print(f"Found {len(results['results'])} results:")
        for i, result in enumerate(results['results'], 1):
            print(f"  {i}. {result['title']}")
            print(f"     Slug: {result['slug']}")
            print(f"     Views: {result['viewCount']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Get a specific page
    print("\n2. Getting page 'United_Petroleum'...")
    try:
        page = client.get_page("United_Petroleum")
        page_data = page['page']
        print(f"Title: {page_data['title']}")
        print(f"Citations: {len(page_data.get('citations', []))}")
        print(f"Images: {len(page_data.get('images', []))}")
        
        # Show first few citations
        if page_data.get('citations'):
            print("\nFirst 3 citations:")
            for citation in page_data['citations'][:3]:
                print(f"  [{citation['id']}] {citation['title']}")
                print(f"      {citation['url']}")
    except GrokipediaNotFoundError:
        print("Page not found!")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Search and get pages
    print("\n3. Searching for 'Python' and getting details...")
    try:
        search_results = client.search_pages("Python", limit=3)
        for result in search_results:
            print(f"\n  Title: {result['title']}")
            print(f"  Relevance Score: {result['relevanceScore']}")
            # Try to get the full page
            try:
                page = client.get_page(result['slug'])
                print(f"  Content length: {len(page['page'].get('content', ''))} characters")
            except Exception as e:
                print(f"  Could not retrieve full page: {e}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Get edit history for a page
    print("\n4. Getting edit history for 'United_States'...")
    try:
        edit_history = client.list_edit_requests_by_slug("United_States", limit=5)
        print(f"Total edit requests: {edit_history.get('totalCount', 0)}")
        print(f"Has more: {edit_history.get('hasMore', False)}")
        print(f"\nShowing first {len(edit_history.get('editRequests', []))} edit requests:")
        for i, edit_request in enumerate(edit_history.get('editRequests', [])[:5], 1):
            print(f"\n  {i}. Status: {edit_request.get('status', 'Unknown')}")
            print(f"     Summary: {edit_request.get('summary', 'N/A')}")
            print(f"     Type: {edit_request.get('type', 'Unknown')}")
            print(f"     Section: {edit_request.get('sectionTitle', 'N/A')}")
            print(f"     Created: {edit_request.get('createdAt', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Using context manager
    print("\n5. Using context manager for automatic cleanup...")
    with GrokipediaClient() as client:
        results = client.search("test", limit=2)
        print(f"Found {len(results['results'])} test results")
    
    print("\nDone!")


if __name__ == "__main__":
    main()

