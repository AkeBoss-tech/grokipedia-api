# Grokipedia API

[![PyPI version](https://badge.fury.io/py/grokipedia-api.svg)](https://badge.fury.io/py/grokipedia-api)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client for accessing content from [Grokipedia](https://grokipedia.com/), an open-source, comprehensive collection of all knowledge.

## Features

- **Search**: Search through Grokipedia's vast collection of articles
- **Page Retrieval**: Get full page content, including headings, text, and citations
- **Structured Data**: Access well-structured data with proper typing
- **Easy to Use**: Simple and intuitive API
- **Async Support**: Fast async/await API with aiohttp for concurrent operations
- **Auto Retries**: Automatic retry logic with exponential backoff
- **Rate Limit Handling**: Built-in rate limit detection and handling
- **MCP Server**: Model Context Protocol server for AI integrations (Python 3.10+)
- **CLI Support**: Command-line interface for quick access

## Installation

### Basic Installation

```bash
pip install grokipedia-api
```

### With Additional Features

For async support:

```bash
pip install grokipedia-api[async]
```

For MCP server functionality (Python 3.10+):

```bash
pip install grokipedia-api[mcp]
```

For all features:

```bash
pip install grokipedia-api[all]
```

Or install from source:

```bash
git clone https://github.com/AkeBoss-tech/grokipedia-api.git
cd grokipedia-api
pip install -e .
```

## Quick Start

### Basic Usage

```python
from grokipedia_api import GrokipediaClient

# Create a client
client = GrokipediaClient()

# Search for articles
results = client.search("Python programming")
print(f"Found {len(results['results'])} results")

# Get a specific page
page = client.get_page("United_Petroleum")
print(f"Title: {page['page']['title']}")
print(f"Content: {page['page']['content'][:200]}...")
```

### Search Functionality

```python
from grokipedia_api import GrokipediaClient

client = GrokipediaClient()

# Search with pagination
results = client.search("machine learning", limit=20, offset=0)
for result in results['results']:
    print(f"- {result['title']}")
    print(f"  Slug: {result['slug']}")
    print(f"  Views: {result['viewCount']}")
    print()
```

### Get Full Page Content

```python
from grokipedia_api import GrokipediaClient

client = GrokipediaClient()

# Get full page with all content
page = client.get_page("United_Petroleum", include_content=True)

# Access structured data
title = page['page']['title']
content = page['page']['content']
citations = page['page']['citations']

print(f"Article: {title}")
print(f"\nCitations: {len(citations)}")
for citation in citations:
    print(f"- [{citation['id']}] {citation['title']}")
    print(f"  {citation['url']}")
```

### Async Usage

For faster, concurrent operations with async/await:

```python
import asyncio
from grokipedia_api import AsyncGrokipediaClient, search_many, get_many_pages

async def main():
    # Basic async usage
    async with AsyncGrokipediaClient() as client:
        results = await client.search("Python programming")
        print(f"Found {len(results['results'])} results")
        
        page = await client.get_page("United_Petroleum")
        print(f"Title: {page['page']['title']}")
    
    # Search multiple queries concurrently
    queries = ["Python", "JavaScript", "Rust"]
    all_results = await search_many(queries, limit=5)
    print(f"Total results: {len(all_results)}")
    
    # Get multiple pages concurrently
    slugs = ["United_Petroleum", "Python_(programming_language)"]
    pages = await get_many_pages(slugs)
    for page_data in pages:
        print(f"✓ {page_data['page']['title']}")

asyncio.run(main())
```

### Automatic Retries

The client automatically retries failed requests with exponential backoff:

```python
from grokipedia_api import GrokipediaClient

client = GrokipediaClient()

# Automatically retries up to 3 times on network errors
results = client.search("machine learning")
```

### Using Context Manager

```python
from grokipedia_api import GrokipediaClient

# Use context manager for automatic cleanup
with GrokipediaClient() as client:
    results = client.search("Python")
    for result in results['results']:
        print(result['title'])
```

### MCP Server (Python 3.10+)

For AI agent integrations:

```bash
# Start the MCP server
grokipedia-mcp
```

The server exposes tools for searching and retrieving Grokipedia content via the Model Context Protocol. See [MCP_SERVER.md](MCP_SERVER.md) for detailed documentation.

### Command Line Interface

```bash
# Search for articles
grokipedia search "Python programming"

# Get a specific page
grokipedia get "United_Petroleum" --citations

# Get full content
grokipedia get "United_Petroleum" --full
```

## API Reference

### GrokipediaClient

The main client class for interacting with Grokipedia.

#### Methods

##### `search(query, limit=12, offset=0)`

Search for articles in Grokipedia.

**Parameters:**
- `query` (str): Search query string
- `limit` (int): Maximum number of results to return (default: 12)
- `offset` (int): Number of results to skip for pagination (default: 0)

**Returns:**
- Dictionary containing:
  - `results`: List of search result dictionaries
  - `total_count`: Total number of results (if available)

**Example:**
```python
results = client.search("Python programming", limit=20)
```

##### `get_page(slug, include_content=True, validate_links=True)`

Get a specific page by its slug.

**Parameters:**
- `slug` (str): Page slug (e.g., "United_Petroleum")
- `include_content` (bool): Whether to include full content (default: True)
- `validate_links` (bool): Whether to validate links (default: True)

**Returns:**
- Dictionary containing:
  - `page`: Page information including title, content, citations, images, etc.
  - `found`: Boolean indicating if the page was found

**Example:**
```python
page = client.get_page("Python_(programming_language)")
```

##### `search_pages(query, limit=12)`

Search for pages and return results as a list.

**Parameters:**
- `query` (str): Search query string
- `limit` (int): Maximum number of results to return (default: 12)

**Returns:**
- List of search result dictionaries

**Example:**
```python
pages = client.search_pages("machine learning")
```

## Data Models

The library provides structured data models for working with Grokipedia content:

- `Page`: Represents a full Grokipedia page
- `Citation`: Represents a citation in an article
- `Image`: Represents an image in an article
- `SearchResult`: Represents a search result

## Error Handling

The library provides custom exceptions:

- `GrokipediaError`: Base exception for all Grokipedia errors
- `GrokipediaNotFoundError`: Raised when a requested resource is not found
- `GrokipediaAPIError`: Raised when there's an API-related error

```python
from grokipedia_api import GrokipediaClient
from grokipedia_api.exceptions import GrokipediaNotFoundError

client = GrokipediaClient()

try:
    page = client.get_page("NonExistentPage")
except GrokipediaNotFoundError:
    print("Page not found!")
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/AkeBoss-tech/grokipedia-api.git
cd grokipedia-api

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=grokipedia_api --cov-report=html
```

### Code Style

This project uses:
- [Black](https://black.readthedocs.io/) for code formatting
- [Ruff](https://ruff.rs/) for linting
- [mypy](https://mypy.readthedocs.io/) for type checking

```bash
# Format code
black grokipedia_api tests

# Lint code
ruff check grokipedia_api tests

# Type check
mypy grokipedia_api
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Grokipedia](https://grokipedia.com/) for providing the amazing knowledge base
- All the contributors and maintainers

## Support

If you encounter any issues or have questions, please open an issue on [GitHub](https://github.com/AkeBoss-tech/grokipedia-api/issues).

## Changelog

### 0.1.0 (2025-01-09)

- Initial release
- Search functionality
- Page retrieval with full content
- Structured data models
- Basic error handling

