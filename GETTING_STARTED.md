# Getting Started with Grokipedia API

Welcome! This guide will help you get started with grokipedia-api quickly.

## Installation

### Quick Install

```bash
pip install grokipedia-api
```

### With MCP Support (Python 3.10+)

For AI agent integrations:

```bash
pip install grokipedia-api[mcp]
```

## Your First Steps

### 1. Try the CLI

The fastest way to get started:

```bash
# Search for articles
grokipedia search "Python programming"

# Get a specific page
grokipedia get "Python_(programming_language)" --citations
```

### 2. Use the Python API

```python
from grokipedia_api import GrokipediaClient

# Create a client
client = GrokipediaClient()

# Search for articles
results = client.search("Python programming", limit=10)
print(f"Found {len(results['results'])} results")

# Get a specific page
page = client.get_page("Python_(programming_language)")
print(f"Title: {page['page']['title']}")
print(f"Citations: {len(page['page']['citations'])}")
```

### 3. Explore MCP Integration

If you have Python 3.10+:

```bash
# Start the MCP server
grokipedia-mcp
```

Then connect with Claude Desktop or any MCP client. See [MCP_SERVER.md](MCP_SERVER.md) for details.

## Common Use Cases

### Search for Articles

```python
from grokipedia_api import GrokipediaClient

client = GrokipediaClient()

# Basic search
results = client.search("artificial intelligence")

# Search with pagination
page1 = client.search("Python", limit=20, offset=0)
page2 = client.search("Python", limit=20, offset=20)

# Search and get results list
pages = client.search_pages("machine learning", limit=5)
for page in pages:
    print(page['title'])
```

### Get Full Page Content

```python
from grokipedia_api import GrokipediaClient

client = GrokipediaClient()

# Get full page
page = client.get_page("United_Petroleum")

# Access different parts
title = page['page']['title']
content = page['page']['content']
citations = page['page']['citations']
images = page['page']['images']

print(f"Article: {title}")
print(f"Citations: {len(citations)}")
print(f"Images: {len(images)}")
```

### Extract Citations

```python
from grokipedia_api import GrokipediaClient

client = GrokipediaClient()
page = client.get_page("Python_(programming_language)")

# Print all citations
for citation in page['page']['citations']:
    print(f"[{citation['id']}] {citation['title']}")
    print(f"  URL: {citation['url']}")
    print()
```

### Batch Operations

```python
from grokipedia_api import GrokipediaClient

client = GrokipediaClient()

# Search for multiple topics
topics = ["Python", "JavaScript", "Go"]

for topic in topics:
    results = client.search(topic, limit=5)
    print(f"\n{topic}: {len(results['results'])} results")
    for result in results['results'][:3]:
        print(f"  - {result['title']}")
```

### Error Handling

```python
from grokipedia_api import GrokipediaClient
from grokipedia_api.exceptions import GrokipediaNotFoundError

client = GrokipediaClient()

try:
    page = client.get_page("ThisPageDoesNotExist123")
except GrokipediaNotFoundError:
    print("Page not found!")
except Exception as e:
    print(f"Error: {e}")
```

## Next Steps

1. **Read the docs:**
   - [README.md](README.md) - Main documentation
   - [USAGE.md](USAGE.md) - Detailed usage guide
   - [MCP_SERVER.md](MCP_SERVER.md) - MCP integration

2. **Try the examples:**
   ```bash
   python example.py
   ```

3. **Explore EXPANSION_PLAN.md** for future features

4. **Share your package:**
   - Tell others: `pip install grokipedia-api`
   - Star on GitHub
   - Share on social media

## Tips

- Use pagination for large result sets
- The `search_pages()` method is a convenience wrapper
- Citations are always included in page data
- Content is in markdown format
- All requests are cached by the session

## Need Help?

- Check [USAGE.md](USAGE.md) for detailed examples
- See [MCP_SERVER.md](MCP_SERVER.md) for AI integrations
- Open an issue on GitHub
- Read the inline documentation

Happy coding! 🚀

