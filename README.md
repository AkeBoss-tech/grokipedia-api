# Grokipedia API

[![PyPI version](https://badge.fury.io/py/grokipedia-api.svg)](https://badge.fury.io/py/grokipedia-api)
[![npm version](https://badge.fury.io/js/grokipedia-api.svg)](https://badge.fury.io/js/grokipedia-api)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 14+](https://img.shields.io/badge/node-14%2B-brightgreen.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/grokipedia-api?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/grokipedia-api)

A client library for accessing content from [Grokipedia](https://grokipedia.com/), an open-source, comprehensive collection of all knowledge.

**Available in both Python and JavaScript/TypeScript!**

---

## Quick Navigation

- [Python](#-python) - [Installation](#python-installation) | [Quick Start](#python-quick-start) | [API Reference](#python-api-reference)
- [JavaScript/TypeScript](#-javascripttypescript) - [Installation](#javascript-installation) | [Quick Start](#javascript-quick-start) | [API Reference](#javascript-api-reference)

---

## Python

### Python Installation

#### Basic Installation

```bash
pip install grokipedia-api
```

#### With Additional Features

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

### Python Quick Start

#### Basic Usage

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

#### Search Functionality

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

#### Get Full Page Content

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

#### Async Usage

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

#### Using Context Manager

```python
from grokipedia_api import GrokipediaClient

# Use context manager for automatic cleanup
with GrokipediaClient() as client:
    results = client.search("Python")
    for result in results['results']:
        print(result['title'])
```

#### MCP Server (Python 3.10+)

For AI agent integrations:

```bash
# Start the MCP server
grokipedia-mcp
```

The server exposes tools for searching and retrieving Grokipedia content via the Model Context Protocol. See [MCP_SERVER.md](MCP_SERVER.md) for detailed documentation.

#### Command Line Interface

```bash
# Search for articles
grokipedia search "Python programming"

# Get a specific page
grokipedia get "United_Petroleum" --citations

# Get full content
grokipedia get "United_Petroleum" --full
```

### Python API Reference

#### GrokipediaClient

The main client class for interacting with Grokipedia.

##### Methods

**`search(query, limit=12, offset=0)`**

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

**`get_page(slug, include_content=True, validate_links=True)`**

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

**`search_pages(query, limit=12)`**

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

### Python Error Handling

The library provides custom exceptions:

- `GrokipediaError`: Base exception for all Grokipedia errors
- `GrokipediaNotFoundError`: Raised when a requested resource is not found
- `GrokipediaAPIError`: Raised when there's an API-related error
- `GrokipediaRateLimitError`: Raised when rate limit is exceeded

```python
from grokipedia_api import GrokipediaClient
from grokipedia_api.exceptions import GrokipediaNotFoundError

client = GrokipediaClient()

try:
    page = client.get_page("NonExistentPage")
except GrokipediaNotFoundError:
    print("Page not found!")
```

---

## JavaScript/TypeScript

### JavaScript Installation

```bash
npm install grokipedia-api
```

Or with yarn:

```bash
yarn add grokipedia-api
```

### JavaScript Quick Start

#### Basic Usage (CommonJS)

```javascript
const { GrokipediaClient } = require('grokipedia-api');

// Create a client
const client = new GrokipediaClient();

// Search for articles
client.search('Python programming')
  .then(results => {
    console.log(`Found ${results.results.length} results`);
    results.results.forEach(result => {
      console.log(`- ${result.title} (${result.slug})`);
    });
  })
  .catch(error => {
    console.error('Error:', error.message);
  });

// Get a specific page
client.getPage('United_Petroleum')
  .then(page => {
    console.log(`Title: ${page.page.title}`);
    console.log(`Content: ${page.page.content.substring(0, 200)}...`);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

#### TypeScript / ES6 Import

```typescript
import { GrokipediaClient } from 'grokipedia-api';

const client = new GrokipediaClient();

// Search for articles
const results = await client.search('machine learning', 20);
console.log(`Found ${results.results.length} results`);

// Get a specific page
const page = await client.getPage('United_Petroleum', true);
console.log(`Title: ${page.page.title}`);
console.log(`Citations: ${page.page.citations?.length || 0}`);
```

#### Async/Await Example

```javascript
const { GrokipediaClient } = require('grokipedia-api');

async function main() {
  const client = new GrokipediaClient();
  
  try {
    // Search with pagination
    const results = await client.search('machine learning', 20, 0);
    console.log(`Total results: ${results.total_count || 'unknown'}`);
    
    for (const result of results.results) {
      console.log(`- ${result.title}`);
      console.log(`  Slug: ${result.slug}`);
      console.log(`  Views: ${result.viewCount || 'N/A'}`);
    }
    
    // Get full page content
    const page = await client.getPage('United_Petroleum', true);
    console.log(`\nArticle: ${page.page.title}`);
    console.log(`\nCitations: ${page.page.citations?.length || 0}`);
    
    if (page.page.citations) {
      page.page.citations.forEach(citation => {
        console.log(`- [${citation.id}] ${citation.title}`);
        console.log(`  ${citation.url}`);
      });
    }
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    client.close();
  }
}

main();
```

#### Advanced Configuration

```javascript
const { GrokipediaClient } = require('grokipedia-api');

// Create client with custom options
const client = new GrokipediaClient({
  baseUrl: 'https://grokipedia.com', // Optional: custom base URL
  timeout: 30000,                    // Request timeout in ms (default: 30000)
  useCache: true,                    // Enable caching (default: true)
  cacheTtl: 604800,                  // Cache TTL in seconds (default: 7 days)
});

// Search for pages (returns just the results array)
const pages = await client.searchPages('Python', 10);
pages.forEach(page => {
  console.log(`${page.title}: ${page.snippet.substring(0, 100)}...`);
});

// Clear cache if needed
client.clearCache();
```

### JavaScript API Reference

#### GrokipediaClient

The main client class for interacting with Grokipedia.

##### Constructor

```typescript
new GrokipediaClient(options?: ClientOptions)
```

**Options:**
- `baseUrl` (string, optional): Custom base URL (default: `https://grokipedia.com`)
- `timeout` (number, optional): Request timeout in milliseconds (default: `30000`)
- `useCache` (boolean, optional): Enable caching (default: `true`)
- `cacheTtl` (number, optional): Cache time-to-live in seconds (default: `604800` = 7 days)

##### Methods

**`search(query, limit?, offset?)`**

Search for articles in Grokipedia.

**Parameters:**
- `query` (string): Search query string
- `limit` (number, optional): Maximum number of results to return (default: `12`)
- `offset` (number, optional): Number of results to skip for pagination (default: `0`)

**Returns:** `Promise<SearchResponse>`

**Example:**
```javascript
const results = await client.search('Python programming', 20);
```

**`getPage(slug, includeContent?, validateLinks?)`**

Get a specific page by its slug.

**Parameters:**
- `slug` (string): Page slug (e.g., `"United_Petroleum"`)
- `includeContent` (boolean, optional): Whether to include full content (default: `true`)
- `validateLinks` (boolean, optional): Whether to validate links (default: `true`)

**Returns:** `Promise<PageResponse>`

**Example:**
```javascript
const page = await client.getPage('Python_(programming_language)');
```

**`searchPages(query, limit?)`**

Search for pages and return results as a list.

**Parameters:**
- `query` (string): Search query string
- `limit` (number, optional): Maximum number of results to return (default: `12`)

**Returns:** `Promise<SearchResult[]>`

**Example:**
```javascript
const pages = await client.searchPages('machine learning');
```

**`clearCache()`**

Clear the in-memory cache.

**Example:**
```javascript
client.clearCache();
```

**`close()`**

Close the client and clean up resources.

**Example:**
```javascript
client.close();
```

### JavaScript TypeScript Types

The package includes full TypeScript definitions. Import types as needed:

```typescript
import {
  GrokipediaClient,
  Page,
  PageResponse,
  SearchResult,
  SearchResponse,
  Citation,
  Image,
  ClientOptions,
} from 'grokipedia-api';
```

### JavaScript Error Handling

The library provides custom exceptions:

- `GrokipediaError`: Base exception for all Grokipedia errors
- `GrokipediaNotFoundError`: Raised when a requested resource is not found
- `GrokipediaAPIError`: Raised when there's an API-related error
- `GrokipediaRateLimitError`: Raised when rate limit is exceeded

```javascript
const { GrokipediaClient, GrokipediaNotFoundError } = require('grokipedia-api');

const client = new GrokipediaClient();

try {
  const page = await client.getPage('NonExistentPage');
} catch (error) {
  if (error instanceof GrokipediaNotFoundError) {
    console.log('Page not found!');
  } else {
    console.error('Error:', error.message);
  }
}
```

---

## Features

Both Python and JavaScript versions include:

- **Search**: Search through Grokipedia's vast collection of articles
- **Page Retrieval**: Get full page content, including headings, text, and citations
- **Structured Data**: Access well-structured data with proper typing
- **Easy to Use**: Simple and intuitive API
- **Auto Retries**: Automatic retry logic with exponential backoff
- **Rate Limit Handling**: Built-in rate limit detection and handling
- **Caching**: Optional caching to reduce API calls

**Python-specific features:**
- **Async Support**: Fast async/await API with aiohttp
- **MCP Server**: Model Context Protocol server for AI integrations
- **CLI Support**: Command-line interface

**JavaScript-specific features:**
- **TypeScript Support**: Full TypeScript definitions included

## Data Models

Both libraries provide structured data models:

- `Page`: Represents a full Grokipedia page
- `Citation`: Represents a citation in an article
- `Image`: Represents an image in an article
- `SearchResult`: Represents a search result

## Development

### Python Development

```bash
# Clone the repository
git clone https://github.com/AkeBoss-tech/grokipedia-api.git
cd grokipedia-api

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black grokipedia_api tests

# Lint code
ruff check grokipedia_api tests
```

### JavaScript Development

```bash
# Clone the repository
git clone https://github.com/AkeBoss-tech/grokipedia-api.git
cd grokipedia-api

# Install dependencies
npm install

# Build TypeScript
npm run build

# Run tests
npm test

# Lint code
npm run lint
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

### 0.3.0 (Python)
- Added async client support
- Added MCP server functionality
- Enhanced error handling

### 0.1.0 (JavaScript)
- Initial npm release
- Full TypeScript support
- Search and page retrieval functionality
