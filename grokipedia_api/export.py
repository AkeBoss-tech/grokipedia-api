"""Export utilities for Grokipedia content."""

import json
import re
from typing import Any, Dict, List, Union


def to_markdown(page: Union[Dict[str, Any], 'Page']) -> str:
    """Convert page to clean markdown.
    
    Args:
        page: Page data (dict or Page model)
        
    Returns:
        Markdown string
    """
    # Handle both dict and model
    if hasattr(page, 'model_dump'):
        # Pydantic model
        data = page.model_dump()
        title = data.get('title', '')
        content = data.get('content', '')
        citations = data.get('citations', [])
        description = data.get('description', '')
    else:
        # Dictionary
        data = page if isinstance(page, dict) else {}
        title = data.get('title', '')
        content = data.get('content', '')
        citations = data.get('citations', [])
        description = data.get('description', '')
    
    # Build markdown
    md = f"# {title}\n\n"
    
    if description:
        md += f"{description}\n\n"
    
    if content:
        # Clean HTML tags
        content_clean = re.sub(r'<[^>]+>', '', content)
        md += content_clean + "\n\n"
    
    # Add citations
    if citations:
        md += "## Citations\n\n"
        for i, citation in enumerate(citations, 1):
            if isinstance(citation, dict):
                cit_title = citation.get('title', '')
                cit_url = citation.get('url', '')
                cit_desc = citation.get('description', '')
            else:
                cit_title = getattr(citation, 'title', '')
                cit_url = getattr(citation, 'url', '')
                cit_desc = getattr(citation, 'description', '')
            
            md += f"{i}. **{cit_title}**\n"
            if cit_desc:
                md += f"   {cit_desc}\n"
            if cit_url:
                md += f"   {cit_url}\n"
            md += "\n"
    
    return md


def to_json(page: Union[Dict[str, Any], 'Page'], indent: int = 2) -> str:
    """Convert page to JSON string.
    
    Args:
        page: Page data (dict or Page model)
        indent: JSON indentation level
        
    Returns:
        JSON string
    """
    # Handle both dict and model
    if hasattr(page, 'model_dump_json'):
        # Pydantic model
        return page.model_dump_json(indent=indent)
    elif hasattr(page, 'model_dump'):
        # Pydantic model, not JSON serializable
        data = page.model_dump()
        return json.dumps(data, indent=indent, ensure_ascii=False)
    else:
        # Dictionary
        return json.dumps(page, indent=indent, ensure_ascii=False, default=str)


def to_html(page: Union[Dict[str, Any], 'Page']) -> str:
    """Convert page to HTML.
    
    Args:
        page: Page data (dict or Page model)
        
    Returns:
        HTML string
    """
    # Handle both dict and model
    if hasattr(page, 'model_dump'):
        # Pydantic model
        data = page.model_dump()
        title = data.get('title', '')
        content = data.get('content', '')
        citations = data.get('citations', [])
        description = data.get('description', '')
    else:
        # Dictionary
        data = page if isinstance(page, dict) else {}
        title = data.get('title', '')
        content = data.get('content', '')
        citations = data.get('citations', [])
        description = data.get('description', '')
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .description {{
            color: #666;
            font-style: italic;
            margin-bottom: 20px;
        }}
        .citation {{
            margin: 10px 0;
            padding: 10px;
            background: #f5f5f5;
            border-left: 4px solid #4CAF50;
        }}
        .citation a {{
            color: #4CAF50;
            text-decoration: none;
        }}
        .citation a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
"""
    
    if description:
        html += f'    <div class="description">{description}</div>\n'
    
    if content:
        html += f"    <div>{content}</div>\n"
    
    if citations:
        html += "    <h2>Citations</h2>\n"
        for citation in citations:
            if isinstance(citation, dict):
                cit_title = citation.get('title', '')
                cit_url = citation.get('url', '')
                cit_desc = citation.get('description', '')
            else:
                cit_title = getattr(citation, 'title', '')
                cit_url = getattr(citation, 'url', '')
                cit_desc = getattr(citation, 'description', '')
            
            html += f'    <div class="citation">\n'
            html += f'        <strong>{cit_title}</strong><br>\n'
            if cit_desc:
                html += f'        {cit_desc}<br>\n'
            if cit_url:
                html += f'        <a href="{cit_url}" target="_blank">{cit_url}</a>\n'
            html += "    </div>\n"
    
    html += """</body>
</html>
"""
    
    return html


def to_plain_text(page: Union[Dict[str, Any], 'Page']) -> str:
    """Convert page to plain text.
    
    Args:
        page: Page data (dict or Page model)
        
    Returns:
        Plain text string
    """
    # Handle both dict and model
    if hasattr(page, 'model_dump'):
        # Pydantic model
        data = page.model_dump()
        title = data.get('title', '')
        content = data.get('content', '')
        citations = data.get('citations', [])
        description = data.get('description', '')
    else:
        # Dictionary
        data = page if isinstance(page, dict) else {}
        title = data.get('title', '')
        content = data.get('content', '')
        citations = data.get('citations', [])
        description = data.get('description', '')
    
    # Build plain text
    text = f"{title}\n"
    text += "=" * len(title) + "\n\n"
    
    if description:
        text += f"{description}\n\n"
    
    if content:
        # Clean HTML tags
        content_clean = re.sub(r'<[^>]+>', '', content)
        text += content_clean + "\n\n"
    
    # Add citations
    if citations:
        text += "CITATIONS\n"
        text += "-" * 50 + "\n"
        for i, citation in enumerate(citations, 1):
            if isinstance(citation, dict):
                cit_title = citation.get('title', '')
                cit_url = citation.get('url', '')
                cit_desc = citation.get('description', '')
            else:
                cit_title = getattr(citation, 'title', '')
                cit_url = getattr(citation, 'url', '')
                cit_desc = getattr(citation, 'description', '')
            
            text += f"{i}. {cit_title}\n"
            if cit_desc:
                text += f"   {cit_desc}\n"
            if cit_url:
                text += f"   {cit_url}\n"
            text += "\n"
    
    return text


def export_to_file(
    page: Union[Dict[str, Any], 'Page'],
    filepath: str,
    format: str = 'markdown'
) -> None:
    """Export page to file in specified format.
    
    Args:
        page: Page data (dict or Page model)
        filepath: Output file path
        format: Export format ('markdown', 'json', 'html', 'txt')
        
    Raises:
        ValueError: If format is not supported
    """
    format = format.lower()
    
    if format == 'markdown' or format == 'md':
        content = to_markdown(page)
    elif format == 'json':
        content = to_json(page)
    elif format == 'html':
        content = to_html(page)
    elif format == 'txt' or format == 'text':
        content = to_plain_text(page)
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'markdown', 'json', 'html', or 'txt'")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

