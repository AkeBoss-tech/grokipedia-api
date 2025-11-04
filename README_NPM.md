# grokipedia-api

[![npm version](https://badge.fury.io/js/grokipedia-api.svg)](https://badge.fury.io/js/grokipedia-api)
[![Node.js 14+](https://img.shields.io/badge/node-14%2B-brightgreen.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Node.js client for accessing content from [Grokipedia](https://grokipedia.com/), an open-source, comprehensive collection of all knowledge.

## Features

- **Search**: Search through Grokipedia's vast collection of articles
- **Page Retrieval**: Get full page content, including headings, text, and citations
- **TypeScript Support**: Full TypeScript definitions included
- **Easy to Use**: Simple and intuitive API
- **Auto Retries**: Automatic retry logic with exponential backoff
- **Rate Limit Handling**: Built-in rate limit detection and handling
- **Caching**: Optional in-memory caching to reduce API calls

## Installation

```bash
npm install grokipedia-api
```

Or with yarn:

```bash
yarn add grokipedia-api
```

## Quick Start

### Basic Usage

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

### TypeScript / ES6 Import

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

### Async/Await Example

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

### Advanced Configuration

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

## API Reference

### GrokipediaClient

The main client class for interacting with Grokipedia.

#### Constructor

```typescript
new GrokipediaClient(options?: ClientOptions)
```

**Options:**
- `baseUrl` (string, optional): Custom base URL (default: `https://grokipedia.com`)
- `timeout` (number, optional): Request timeout in milliseconds (default: `30000`)
- `useCache` (boolean, optional): Enable caching (default: `true`)
- `cacheTtl` (number, optional): Cache time-to-live in seconds (default: `604800` = 7 days)

#### Methods

##### `search(query, limit?, offset?)`

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

##### `getPage(slug, includeContent?, validateLinks?)`

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

##### `searchPages(query, limit?)`

Search for pages and return results as a list.

**Parameters:**
- `query` (string): Search query string
- `limit` (number, optional): Maximum number of results to return (default: `12`)

**Returns:** `Promise<SearchResult[]>`

**Example:**
```javascript
const pages = await client.searchPages('machine learning');
```

##### `clearCache()`

Clear the in-memory cache.

**Example:**
```javascript
client.clearCache();
```

##### `close()`

Close the client and clean up resources.

**Example:**
```javascript
client.close();
```

## TypeScript Types

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

## Error Handling

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

## Automatic Retries

The client automatically retries failed requests with exponential backoff:

- Up to 3 retry attempts
- Exponential backoff (1s, 2s, 4s)
- Maximum delay of 10 seconds
- Does not retry on 404 errors or non-rate-limit API errors

## Caching

The client includes optional in-memory caching:

- Enabled by default
- Cache TTL: 7 days (configurable)
- Caches both search results and page content
- Use `clearCache()` to manually clear the cache

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Grokipedia](https://grokipedia.com/) for providing the amazing knowledge base
- All the contributors and maintainers

## Support

If you encounter any issues or have questions, please open an issue on [GitHub](https://github.com/AkeBoss-tech/grokipedia-api/issues).

## Related

- [Python version](https://pypi.org/project/grokipedia-api/) - Python client for Grokipedia API


