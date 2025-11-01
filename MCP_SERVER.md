# Grokipedia MCP Server

The Grokipedia API package includes an MCP (Model Context Protocol) server that allows AI agents and other MCP clients to interact with Grokipedia's vast knowledge base.

## Installation

### Basic Installation

```bash
pip install grokipedia-api
```

### With MCP Support

For Python 3.10+ users who want MCP server functionality:

```bash
pip install grokipedia-api[mcp]
```

**Note:** MCP server requires Python 3.10 or higher due to MCP package dependencies.

## Available MCP Tools

The server exposes two main tools:

### 1. `grokipedia_search`

Search for articles in Grokipedia.

**Parameters:**
- `query` (required): Search query string
- `limit` (optional): Maximum number of results (default: 12)
- `offset` (optional): Number of results to skip for pagination (default: 0)

**Returns:**
Formatted search results with title, slug, views, relevance score, and snippet for each result.

### 2. `grokipedia_get_page`

Get a specific page from Grokipedia by its slug.

**Parameters:**
- `slug` (required): Page slug (e.g., "United_Petroleum")
- `include_content` (optional): Whether to include full content (default: true)
- `validate_links` (optional): Whether to validate links (default: true)

**Returns:**
Complete page information including title, citations, images, and content.

## Running the MCP Server

### Standalone Mode

```bash
grokipedia-mcp
```

The server will start and listen on stdin/stdout for MCP protocol messages.

### Integration with AI Frameworks

#### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "grokipedia": {
      "command": "grokipedia-mcp"
    }
  }
}
```

#### Python Script

```python
import subprocess
import json

# Start the MCP server
process = subprocess.Popen(
    ["grokipedia-mcp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Example: List available tools
init_message = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
}

process.stdin.write(json.dumps(init_message).encode() + b"\n")
response = json.loads(process.stdout.readline())
print(response)
```

## Example Usage

### Search for Articles

```python
# Through MCP protocol
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "grokipedia_search",
    "arguments": {
      "query": "Python programming",
      "limit": 5
    }
  }
}
```

**Response:**
```
Found 5 results for 'Python programming':

1. **Python (programming language)**
   - Slug: Python_(programming_language)
   - Views: 2584037
   - Relevance: 1234.56
   - Snippet: Python is a high-level, general-purpose programming...

2. **Python syntax and semantics**
   - Slug: Python_syntax_and_semantics
   - Views: 59180
   - Relevance: 789.01
   ...
```

### Get a Page

```python
# Through MCP protocol
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "grokipedia_get_page",
    "arguments": {
      "slug": "United_Petroleum"
    }
  }
}
```

**Response:**
```
# United Petroleum

**Slug:** United_Petroleum

## Citations (93)

- [1] **United Petroleum - For the love of driving in Australia**
  - URL: https://www.unitedpetroleum.com.au/
  - United Petroleum is an independent, 100% Australian owned fuel...

- [2] **United Petroleum 2025 Company Profile - PitchBook**
  - URL: https://pitchbook.com/profiles/company/58857-22
  ...

## Images (5)

- **United Petroleum station in Kewdale**
  - URL: ./_assets_/United_Petroleum%2C_Kewdale.jpg

## Content

United Petroleum Pty Ltd is an independent Australian fuel retailer...
```

## Integration Examples

### With Claude Desktop

1. Install the package: `pip install grokipedia-api[mcp]`
2. Edit Claude Desktop config as shown above
3. Restart Claude Desktop
4. In Claude, you can now ask: "Search Grokipedia for Python programming articles"
5. Claude will use the MCP tools automatically

### With Custom MCP Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters

async def main():
    # Connect to Grokipedia MCP server
    server_params = StdioServerParameters(
        command="grokipedia-mcp",
        args=[]
    )
    
    async with ClientSession(server_params) as session:
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {[t.name for t in tools.tools]}")
        
        # Call search tool
        result = await session.call_tool(
            "grokipedia_search",
            {"query": "machine learning", "limit": 3}
        )
        print(result.content)

asyncio.run(main())
```

### With Agno Framework

```python
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

async def run_agent():
    server_params = StdioServerParameters(
        command="grokipedia-mcp",
        args=[]
    )
    
    async with MCPTools(server_params=server_params) as mcp_tools:
        agent = Agent(
            name="Grokipedia Assistant",
            tools=[mcp_tools],
            instructions="You help users search and explore Grokipedia content."
        )
        
        await agent.run("Search for Python programming tutorials")

asyncio.run(run_agent())
```

## Error Handling

The server handles errors gracefully:

- **Unknown tool**: Returns error message
- **GrokipediaError**: Returns formatted error from API
- **Missing parameters**: Returns helpful error message
- **Network errors**: Handled by underlying client

Example error response:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Grokipedia error: Page not found: InvalidSlug"
    }
  ]
}
```

## Configuration

The MCP server uses the same configuration as the regular client:

- Base URL: `https://grokipedia.com` (default)
- Timeout: 30 seconds (default)
- No authentication required

## Troubleshooting

### "MCP is not available" Error

**Problem:** Running on Python < 3.10 or without the `mcp` package.

**Solution:** 
```bash
# Check Python version
python --version  # Should be 3.10+

# Install with MCP support
pip install grokipedia-api[mcp]
```

### "Command not found: grokipedia-mcp"

**Problem:** The package isn't installed or the script entry point isn't in PATH.

**Solution:**
```bash
# Reinstall the package
pip install -e .

# Or run directly with Python
python -m grokipedia_api.mcp_server
```

### Server Crashes on Startup

**Problem:** MCP dependencies missing or incompatible.

**Solution:**
```bash
# Full clean install
pip uninstall grokipedia-api
pip install grokipedia-api[mcp]

# Verify installation
grokipedia-mcp --help  # or just grokipedia-mcp to test
```

## Advanced Usage

### Custom Configuration

The MCP server uses the default client settings. To customize:

1. Fork the repository
2. Modify `grokipedia_api/mcp_server.py`
3. Update client initialization in `call_tool()` function

### Adding More Tools

You can extend the MCP server with additional tools:

```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    tools = [...]  # existing tools
    
    # Add your custom tool
    tools.append(
        Tool(
            name="my_custom_tool",
            description="My custom Grokipedia tool",
            inputSchema={...}
        )
    )
    
    return tools
```

### Monitoring and Logging

Enable logging for debugging:

```bash
grokipedia-mcp 2>&1 | tee mcp.log
```

## Performance

- **Search queries**: ~100-500ms typical response time
- **Page retrieval**: ~200-800ms typical response time
- **Concurrent requests**: Handled by client's session pooling

## Security

- The MCP server exposes the same API as the regular client
- No authentication required (public API)
- Read-only access (no data modification)
- All requests use HTTPS
- User-Agent header included with requests

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Grokipedia Website](https://grokipedia.com/)
- [GitHub Repository](https://github.com/AkeBoss-tech/grokipedia-api)

## Contributing

Contributions to the MCP server are welcome! See the main project README for contribution guidelines.

