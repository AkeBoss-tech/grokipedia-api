# Grokipedia API - Project Summary

## Overview

This project provides a Python API client for accessing content from [Grokipedia](https://grokipedia.com/), an open-source, comprehensive collection of knowledge. The API allows users to search for articles and retrieve full page content including headings, text, citations, and other metadata.

## Features

✅ **Search Functionality**: Search through Grokipedia's vast article database  
✅ **Page Retrieval**: Get full page content with headings, text, and citations  
✅ **Citation Extraction**: Access all source citations for articles  
✅ **Image Data**: Retrieve image information from pages  
✅ **Structured Data Models**: Work with well-typed data structures  
✅ **Command-Line Interface**: Use via CLI or Python API  
✅ **Error Handling**: Comprehensive exception handling  
✅ **Documentation**: Complete README and usage examples  

## Package Structure

```
grokipedia-api/
├── grokipedia_api/          # Main package
│   ├── __init__.py         # Package initialization
│   ├── client.py           # Main client class
│   ├── models.py           # Data models
│   ├── exceptions.py       # Custom exceptions
│   └── cli.py              # Command-line interface
├── tests/                   # Unit tests
│   ├── test_client.py
│   └── test_models.py
├── example.py               # Usage examples
├── requirements.txt         # Dependencies
├── pyproject.toml           # Modern Python packaging
├── README.md                # Project documentation
├── USAGE.md                 # Usage guide
├── LICENSE                  # MIT License
└── .gitignore              # Git ignore rules
```

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/grokipedia-api.git
cd grokipedia-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

## Quick Start

### Python API

```python
from grokipedia_api import GrokipediaClient

# Initialize client
client = GrokipediaClient()

# Search for articles
results = client.search("Python programming", limit=10)

# Get a specific page
page = client.get_page("United_Petroleum")
print(page['page']['title'])
print(f"Citations: {len(page['page']['citations'])}")
```

### Command Line

```bash
# Search
grokipedia search "Python programming" --limit 10

# Get page
grokipedia get "United_Petroleum" --citations

# Get full content
grokipedia get "United_Petroleum" --full
```

## API Methods

### GrokipediaClient.search(query, limit=12, offset=0)
Search for articles with pagination support.

### GrokipediaClient.get_page(slug, include_content=True, validate_links=True)
Get full page content including all citations, images, and metadata.

### GrokipediaClient.search_pages(query, limit=12)
Convenience method returning search results as a list.

## Testing

All tests pass successfully:

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=grokipedia_api --cov-report=html
```

## Documentation

- **README.md**: Complete project documentation
- **USAGE.md**: Detailed usage guide with examples
- **example.py**: Working examples of all features

## Dependencies

- **requests** (>=2.31.0): HTTP library for API calls

## Development

The project follows modern Python packaging standards:
- Uses `pyproject.toml` for configuration
- Type hints throughout
- Comprehensive error handling
- Clean code structure
- Full test coverage

## License

MIT License - see LICENSE file for details.

## Author

Created following modern Python packaging best practices and Grokipedia's API structure analysis.

