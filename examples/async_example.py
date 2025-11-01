"""Example demonstrating async usage of Grokipedia API."""

import asyncio

try:
    from grokipedia_api import AsyncGrokipediaClient, search_many, get_many_pages
except ImportError:
    print("Async support requires 'aiohttp'. Install with: pip install grokipedia-api[async]")
    exit(1)


async def main():
    """Demonstrate async features."""
    print("🚀 Grokipedia API - Async Example\n")
    
    # Example 1: Basic async usage with context manager
    print("1. Basic async search:")
    async with AsyncGrokipediaClient(timeout=60) as client:
        results = await client.search("Python", limit=3)
        for i, result in enumerate(results["results"][:3], 1):
            print(f"   {i}. {result['title']} ({result['slug']})")
    
    print()
    
    # Example 2: Get page content
    print("2. Get page content:")
    async with AsyncGrokipediaClient(timeout=60) as client:
        page = await client.get_page("Python_(programming_language)")
        print(f"   Title: {page['page']['title']}")
        print(f"   Citations: {len(page['page']['citations'])}")
        print(f"   Content length: {len(page['page']['content'])} chars")
    
    print()
    
    # Example 3: Concurrent searches
    print("3. Concurrent searches:")
    queries = ["Python", "JavaScript", "Rust", "Go"]
    results = await search_many(queries, limit=2)
    print(f"   Found {len(results)} total results across {len(queries)} queries")
    
    print()
    
    # Example 4: Get multiple pages concurrently
    print("4. Get multiple pages concurrently:")
    slugs = ["Python_(programming_language)", "JavaScript", "Rust_(programming_language)"]
    pages = await get_many_pages(slugs, include_content=False)
    for page_data in pages:
        print(f"   ✓ {page_data['page']['title']}")
    
    print("\n✅ All async examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

