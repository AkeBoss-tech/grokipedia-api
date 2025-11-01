"""MCP server for Grokipedia API.

Note: MCP server requires Python 3.10+ and the 'mcp' package.
Install with: pip install grokipedia-api[mcp]
"""

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Create dummy classes to avoid errors
    Server = None
    stdio_server = None
    Tool = None
    TextContent = None

import sys
from typing import Any, Sequence
from .client import GrokipediaClient
from .exceptions import GrokipediaError

# Only create server if MCP is available
if MCP_AVAILABLE:
    # Create the MCP server
    server = Server("grokipedia-api")
    
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="grokipedia_search",
                description="Search for articles in Grokipedia",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query string"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 12)",
                            "default": 12
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Number of results to skip for pagination (default: 0)",
                            "default": 0
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="grokipedia_get_page",
                description="Get a specific page from Grokipedia by its slug",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "slug": {
                            "type": "string",
                            "description": "Page slug (e.g., 'United_Petroleum')"
                        },
                        "include_content": {
                            "type": "boolean",
                            "description": "Whether to include full content (default: true)",
                            "default": True
                        },
                        "validate_links": {
                            "type": "boolean",
                            "description": "Whether to validate links (default: true)",
                            "default": True
                        }
                    },
                    "required": ["slug"]
                }
            )
        ]
    
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None) -> Sequence[TextContent]:
        """Handle tool calls."""
        if arguments is None:
            arguments = {}
        
        # Create client instance
        client = GrokipediaClient()
        
        try:
            if name == "grokipedia_search":
                query = arguments.get("query", "")
                limit = arguments.get("limit", 12)
                offset = arguments.get("offset", 0)
                
                if not query:
                    raise ValueError("Query parameter is required")
                
                results = client.search(query=query, limit=limit, offset=offset)
                
                # Format results nicely
                output = f"Found {len(results.get('results', []))} results for '{query}':\n\n"
                
                for i, result in enumerate(results.get('results', []), 1):
                    output += f"{i}. **{result.get('title', 'N/A')}**\n"
                    output += f"   - Slug: {result.get('slug', 'N/A')}\n"
                    output += f"   - Views: {result.get('viewCount', '0')}\n"
                    output += f"   - Relevance: {result.get('relevanceScore', 0):.2f}\n"
                    if result.get('snippet'):
                        snippet = result.get('snippet', '').replace('<em>', '**').replace('</em>', '**')
                        # Remove other HTML tags
                        import re
                        snippet = re.sub(r'<[^>]+>', '', snippet)
                        output += f"   - Snippet: {snippet[:100]}...\n" if len(snippet) > 100 else f"   - Snippet: {snippet}\n"
                    output += "\n"
                
                return [TextContent(type="text", text=output)]
            
            elif name == "grokipedia_get_page":
                slug = arguments.get("slug", "")
                include_content = arguments.get("include_content", True)
                validate_links = arguments.get("validate_links", True)
                
                if not slug:
                    raise ValueError("Slug parameter is required")
                
                page_data = client.get_page(
                    slug=slug,
                    include_content=include_content,
                    validate_links=validate_links
                )
                
                page = page_data.get('page', {})
                
                # Format page data nicely
                output = f"# {page.get('title', 'N/A')}\n\n"
                output += f"**Slug:** {page.get('slug', 'N/A')}\n\n"
                
                if page.get('description'):
                    output += f"{page.get('description', '')}\n\n"
                
                citations = page.get('citations', [])
                if citations:
                    output += f"## Citations ({len(citations)})\n\n"
                    for citation in citations[:10]:  # Show first 10
                        output += f"- [{citation.get('id')}] **{citation.get('title', 'N/A')}**\n"
                        output += f"  - URL: {citation.get('url', 'N/A')}\n"
                        if citation.get('description'):
                            desc = citation.get('description', '')[:150]
                            output += f"  - {desc}...\n"
                    if len(citations) > 10:
                        output += f"\n*... and {len(citations) - 10} more citations*\n"
                
                images = page.get('images', [])
                if images:
                    output += f"\n## Images ({len(images)})\n\n"
                    for img in images[:5]:  # Show first 5
                        output += f"- **{img.get('caption', 'N/A')}**\n"
                        output += f"  - URL: {img.get('url', 'N/A')}\n"
                
                if include_content and page.get('content'):
                    content = page.get('content', '')
                    # Truncate if too long
                    if len(content) > 2000:
                        output += f"\n## Content Preview\n\n{content[:2000]}...\n\n"
                        output += f"*Content truncated. Full content has {len(content)} characters*\n"
                    else:
                        output += f"\n## Content\n\n{content}\n"
                
                return [TextContent(type="text", text=output)]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        except GrokipediaError as e:
            return [TextContent(type="text", text=f"Grokipedia error: {str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    
    async def main():
        """Run the MCP server."""
        if not MCP_AVAILABLE:
            print("Error: MCP is not available. Install with: pip install grokipedia-api[mcp]", file=sys.stderr)
            sys.exit(1)
        
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    
    
    if __name__ == "__main__":
        import asyncio
        asyncio.run(main())

else:
    # Fallback if MCP is not available
    async def main():
        """Run the MCP server."""
        print("Error: MCP is not available. Requires Python 3.10+ and the 'mcp' package.", file=sys.stderr)
        print("Install with: pip install grokipedia-api[mcp]", file=sys.stderr)
        sys.exit(1)
    
    if __name__ == "__main__":
        import asyncio
        asyncio.run(main())
