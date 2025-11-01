"""LangChain integration utilities for Grokipedia."""

try:
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Create dummy Document class
    class Document:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "LangChain support requires 'langchain'. "
                "Install with: pip install grokipedia-api[langchain]"
            )

from typing import Any, Dict, List, Optional, Union


def to_langchain_document(
    page: Union[Dict[str, Any], 'Page'],
    metadata_extra: Optional[Dict[str, Any]] = None
) -> Document:
    """Convert page to LangChain Document for RAG.
    
    Args:
        page: Page data (dict or Page model)
        metadata_extra: Additional metadata to include
        
    Returns:
        LangChain Document
        
    Raises:
        ImportError: If langchain is not installed
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "LangChain support requires 'langchain'. "
            "Install with: pip install grokipedia-api[langchain]"
        )
    
    # Handle both dict and model
    if hasattr(page, 'model_dump'):
        # Pydantic model
        data = page.model_dump()
    else:
        # Dictionary
        data = page if isinstance(page, dict) else {}
    
    # Extract content
    if isinstance(page, dict):
        # Handle dict response format
        page_data = data.get('page', data)
        title = page_data.get('title', '')
        content = page_data.get('content', '')
        slug = page_data.get('slug', '')
        description = page_data.get('description', '')
        citations = page_data.get('citations', [])
    else:
        # Handle page model
        title = data.get('title', '')
        content = data.get('content', '')
        slug = data.get('slug', '')
        description = data.get('description', '')
        citations = data.get('citations', [])
    
    # Build document content
    doc_content = f"# {title}\n\n"
    if description:
        doc_content += f"{description}\n\n"
    doc_content += content
    
    # Build metadata
    metadata = {
        'title': title,
        'slug': slug,
        'source': f'grokipedia:{slug}',
        'source_type': 'grokipedia',
        'citation_count': len(citations) if isinstance(citations, list) else 0
    }
    
    # Add citations to metadata if available
    if citations:
        metadata['citations'] = [
            {'title': c.get('title', '') if isinstance(c, dict) else getattr(c, 'title', ''),
             'url': c.get('url', '') if isinstance(c, dict) else getattr(c, 'url', '')}
            for c in citations
        ]
    
    # Add extra metadata
    if metadata_extra:
        metadata.update(metadata_extra)
    
    return Document(page_content=doc_content, metadata=metadata)


def search_to_documents(
    search_results: Union[Dict[str, Any], List],
    limit: Optional[int] = None
) -> List[Document]:
    """Convert search results to LangChain Documents.
    
    Args:
        search_results: Search results (dict or list)
        limit: Maximum number of results to convert
        
    Returns:
        List of LangChain Documents
        
    Raises:
        ImportError: If langchain is not installed
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "LangChain support requires 'langchain'. "
            "Install with: pip install grokipedia-api[langchain]"
        )
    
    # Handle both dict and list formats
    if isinstance(search_results, dict):
        results = search_results.get('results', [])
    elif isinstance(search_results, list):
        results = search_results
    else:
        results = []
    
    # Limit results
    if limit is not None:
        results = results[:limit]
    
    documents = []
    for result in results:
        # Build document from search result
        title = result.get('title', '') if isinstance(result, dict) else getattr(result, 'title', '')
        slug = result.get('slug', '') if isinstance(result, dict) else getattr(result, 'slug', '')
        snippet = result.get('snippet', '') if isinstance(result, dict) else getattr(result, 'snippet', '')
        relevance = result.get('relevanceScore', 0) if isinstance(result, dict) else getattr(result, 'relevanceScore', 0)
        views = result.get('viewCount', '0') if isinstance(result, dict) else getattr(result, 'viewCount', '0')
        
        doc_content = f"## {title}\n\n{snippet}"
        
        metadata = {
            'title': title,
            'slug': slug,
            'source': f'grokipedia:{slug}',
            'source_type': 'grokipedia_search',
            'relevance_score': relevance,
            'view_count': views,
            'is_search_result': True
        }
        
        documents.append(Document(page_content=doc_content, metadata=metadata))
    
    return documents


def get_relevant_citations(page: Union[Dict[str, Any], 'Page']) -> List[Dict[str, Any]]:
    """Extract citations from page for LangChain metadata.
    
    Args:
        page: Page data (dict or Page model)
        
    Returns:
        List of citation dictionaries
    """
    # Handle both dict and model
    if hasattr(page, 'model_dump'):
        # Pydantic model
        data = page.model_dump()
    else:
        # Dictionary
        data = page if isinstance(page, dict) else {}
    
    citations = data.get('citations', [])
    if not isinstance(citations, list):
        return []
    
    return [
        {
            'title': c.get('title', '') if isinstance(c, dict) else getattr(c, 'title', ''),
            'url': c.get('url', '') if isinstance(c, dict) else getattr(c, 'url', ''),
            'description': c.get('description', '') if isinstance(c, dict) else getattr(c, 'description', '')
        }
        for c in citations
    ]

