"""Command-line interface for Grokipedia API."""

import argparse
import sys
import json
from typing import Optional
from .client import GrokipediaClient
from .exceptions import GrokipediaError


def search_command(args):
    """Execute search command."""
    try:
        with GrokipediaClient() as client:
            results = client.search(
                query=args.query,
                limit=args.limit,
                offset=args.offset
            )
            
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"\nFound {len(results.get('results', []))} results for '{args.query}':\n")
                for i, result in enumerate(results.get('results', []), 1):
                    print(f"{i}. {result.get('title', 'N/A')}")
                    print(f"   Slug: {result.get('slug', 'N/A')}")
                    print(f"   Views: {result.get('viewCount', '0')}")
                    if args.snippet:
                        snippet = result.get('snippet', '')
                        # Remove HTML tags from snippet
                        import re
                        snippet = re.sub(r'<[^>]+>', '', snippet)
                        print(f"   Snippet: {snippet[:100]}...")
                    print()
    except GrokipediaError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def get_page_command(args):
    """Execute get page command."""
    try:
        with GrokipediaClient() as client:
            page_data = client.get_page(
                slug=args.slug,
                include_content=args.content,
                validate_links=args.validate_links
            )
            
            if args.json:
                print(json.dumps(page_data, indent=2))
            else:
                page = page_data['page']
                print(f"\n{page['title']}")
                print("=" * len(page['title']))
                
                if args.content:
                    print(f"\nContent:")
                    print("-" * 50)
                    content = page.get('content', '')
                    # Limit content if not full flag
                    if not args.full and len(content) > 500:
                        print(content[:500] + "...\n[Content truncated. Use --full to see complete content]")
                    else:
                        print(content)
                
                print(f"\nCitations: {len(page.get('citations', []))}")
                if args.citations:
                    for citation in page.get('citations', []):
                        print(f"\n[{citation['id']}] {citation['title']}")
                        print(f"  {citation['url']}")
                        if citation.get('description'):
                            print(f"  {citation['description'][:150]}...")
                
                print(f"\nImages: {len(page.get('images', []))}")
                
                if page.get('stats'):
                    stats = page['stats']
                    print(f"\nStatistics:")
                    print(f"  Total Views: {stats.get('totalViews', '0')}")
                    print(f"  Daily Average: {stats.get('dailyAvgViews', 0):.2f}")
    except GrokipediaError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main(args: Optional[list] = None):
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Grokipedia API - Search and retrieve content from Grokipedia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "Python programming"
  %(prog)s search "machine learning" --limit 20
  %(prog)s get "United_Petroleum" --citations
  %(prog)s get "Python_(programming_language)" --full
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for articles')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=12, help='Maximum number of results (default: 12)')
    search_parser.add_argument('--offset', type=int, default=0, help='Number of results to skip (default: 0)')
    search_parser.add_argument('--json', action='store_true', help='Output JSON format')
    search_parser.add_argument('--snippet', action='store_true', help='Show snippet in results')
    search_parser.set_defaults(func=search_command)
    
    # Get page command
    get_parser = subparsers.add_parser('get', help='Get a specific page by slug')
    get_parser.add_argument('slug', help='Page slug (e.g., "United_Petroleum")')
    get_parser.add_argument('--content', action='store_true', default=True, help='Include full content (default: True)')
    get_parser.add_argument('--no-content', dest='content', action='store_false', help='Exclude content')
    get_parser.add_argument('--validate-links', action='store_true', default=True, help='Validate links (default: True)')
    get_parser.add_argument('--no-validate-links', dest='validate_links', action='store_false', help='Do not validate links')
    get_parser.add_argument('--citations', action='store_true', help='Show citations')
    get_parser.add_argument('--full', action='store_true', help='Show full content without truncation')
    get_parser.add_argument('--json', action='store_true', help='Output JSON format')
    get_parser.set_defaults(func=get_page_command)
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the appropriate command
    parsed_args.func(parsed_args)


if __name__ == "__main__":
    main()

