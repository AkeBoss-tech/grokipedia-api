#!/usr/bin/env python3
"""
Example: Using Grokipedia MCP Server

This example demonstrates how to use the Grokipedia API through the MCP server.

Note: This example requires Python 3.10+ and grokipedia-api[mcp]
Install with: pip install grokipedia-api[mcp]
"""

import asyncio
try:
    from mcp import ClientSession, StdioServerParameters
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Error: MCP not available. Install with: pip install grokipedia-api[mcp]")
    print("Note: Requires Python 3.10+")
    exit(1)


async def main():
    """Example using Grokipedia MCP server."""
    print("Starting Grokipedia MCP Server...")
    
    # Connect to Grokipedia MCP server
    server_params = StdioServerParameters(
        command="grokipedia-mcp",
        args=[]
    )
    
    async with ClientSession(server_params) as session:
        # List available tools
        print("\n1. Listing available tools...")
        tools = await session.list_tools()
        print(f"   Available tools: {[t.name for t in tools.tools]}")
        
        # Search for articles
        print("\n2. Searching for 'Python programming'...")
        search_result = await session.call_tool(
            "grokipedia_search",
            {"query": "Python programming", "limit": 3}
        )
        print("   Results:")
        for content in search_result.content:
            # Show first 500 chars of results
            print(content.text[:500])
        
        # Get a specific page
        print("\n3. Getting page 'Python_(programming_language)'...")
        page_result = await session.call_tool(
            "grokipedia_get_page",
            {"slug": "Python_(programming_language)", "include_content": True}
        )
        print("   Page retrieved:")
        for content in page_result.content:
            # Show first 300 chars
            print(content.text[:300])
        
        print("\n✓ MCP server example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

