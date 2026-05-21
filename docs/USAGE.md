# Grokipedia API - Usage Guide

## Installation

```bash
# Install from source
git clone https://github.com/yourusername/grokipedia-api.git
cd grokipedia-api
pip install -e .
```

## Quick Start

### Python API

```python
from grokipedia_api import GrokipediaClient

# Create a client
client = GrokipediaClient()

# Search for articles
results = client.search("Python programming", limit=10)

# Get a specific page
page = client.get_page("United_Petroleum")
```

### Command Line Interface

```bash
# Search for articles
grokipedia search "Python programming" --limit 10

# Get a specific page
grokipedia get "United_Petroleum" --citations

# Get full content
grokipedia get "United_Petroleum" --full
```

## API Methods

### GrokipediaClient.search()

Search for articles in Grokipedia.

**Parameters:**
- `query` (str): Search query string
- `limit` (int): Maximum number of results (default: 12)
- `offset` (int): Skip results for pagination (default: 0)

**Returns:**
Dictionary with `results` list containing:
- `title`: Article title
- `slug`: Page slug (for get_page)
- `snippet`: Content snippet
- `relevanceScore`: Search relevance
- `viewCount`: Number of views

**Example:**
```python
results = client.search("machine learning", limit=20, offset=0)
for result in results['results']:
    print(f"{result['title']} (Views: {result['viewCount']})")
```

### GrokipediaClient.get_page()

Get full content of a specific page.

**Parameters:**
- `slug` (str): Page slug (e.g., "United_Petroleum")
- `include_content` (bool): Include full content (default: True)
- `validate_links` (bool): Validate links (default: True)

**Returns:**
Dictionary with:
- `page`: Page data including:
  - `title`: Page title
  - `content`: Full markdown content
  - `citations`: List of citation dictionaries
  - `images`: List of image dictionaries
  - `metadata`: Page metadata
  - `stats`: Page statistics
- `found`: Boolean indicating success

**Example:**
```python
page = client.get_page("Python_(programming_language)")
print(page['page']['title'])
print(f"Citations: {len(page['page']['citations'])}")
```

### GrokipediaClient.search_pages()

Convenience method to search and return results as a list.

**Example:**
```python
pages = client.search_pages("Python", limit=5)
for page in pages:
    print(page['title'])
```

## Data Extraction

### Getting Citations

```python
page = client.get_page("United_Petroleum")
citations = page['page']['citations']
for citation in citations:
    print(f"[{citation['id']}] {citation['title']}")
    print(f"URL: {citation['url']}")
    print(f"Description: {citation['description']}")
```

### Getting Images

```python
page = client.get_page("United_Petroleum")
images = page['page']['images']
for image in images:
    print(f"{image['caption']}")
    print(f"URL: {image['url']}")
```

### Extracting Headings and Text

The content is returned in markdown format:

```python
page = client.get_page("United_Petroleum")
content = page['page']['content']

# Parse markdown if needed
import re
headings = re.findall(r'^##?\s+(.+)$', content, re.MULTILINE)
```

### Using Structured Models

The library provides dataclasses for structured access:

```python
from grokipedia_api.models import Page, Citation

page_data = client.get_page("United_Petroleum")
page = Page.from_dict(page_data)

print(f"Title: {page.title}")
print(f"Slug: {page.slug}")
print(f"Citations: {len(page.citations)}")
```

## Error Handling

```python
from grokipedia_api.exceptions import (
    GrokipediaError,
    GrokipediaNotFoundError,
    GrokipediaAPIError
)

try:
    page = client.get_page("NonExistentPage")
except GrokipediaNotFoundError:
    print("Page not found")
except GrokipediaAPIError as e:
    print(f"API error: {e}")
except GrokipediaError as e:
    print(f"General error: {e}")
```

## Advanced Usage

### Pagination

```python
offset = 0
limit = 20
all_results = []

while True:
    results = client.search("Python", limit=limit, offset=offset)
    all_results.extend(results['results'])
    
    if len(results['results']) < limit:
        break
    
    offset += limit
```

### Using Context Manager

```python
# Automatic cleanup
with GrokipediaClient() as client:
    results = client.search("test")
    # Session closed automatically
```

### Custom Configuration

```python
# Custom base URL and timeout
client = GrokipediaClient(
    base_url="https://custom-grokipedia.com",
    timeout=60
)
```

## CLI Examples

```bash
# Basic search
grokipedia search "Python programming"

# Search with snippet
grokipedia search "machine learning" --snippet --limit 10

# Get page
grokipedia get "United_Petroleum"

# Get page with citations
grokipedia get "United_Petroleum" --citations

# Get full content
grokipedia get "United_Petroleum" --full

# JSON output
grokipedia search "test" --json

# Pagination
grokipedia search "Python" --limit 50 --offset 0
```

## Tips

1. **Cache Results**: Consider caching frequently accessed pages
2. **Rate Limiting**: Be respectful with request frequency
3. **Error Handling**: Always handle errors gracefully
4. **Batch Operations**: Use search results to batch retrieve pages
5. **Content Format**: Content is in markdown, parse as needed

## Examples

See `example.py` for a complete working example demonstrating all features.

