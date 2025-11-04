#!/usr/bin/env python3
"""
Script to scrape all pages from Grokipedia (~1M pages).

This script uses a combination of strategies to discover and scrape all pages:
1. Broad search queries (single letters, common prefixes, numbers)
2. Pagination through all search results
3. Async operations for efficiency
4. Progress tracking and resume capability
5. Rate limit handling

Usage:
    python scrape_all_pages.py [--output-dir OUTPUT_DIR] [--resume] [--max-workers MAX_WORKERS]
"""

import asyncio
import json
import argparse
import time
import os
from pathlib import Path
from typing import Set, List, Dict, Any, Optional
from datetime import datetime
import sys

try:
    from grokipedia_api import AsyncGrokipediaClient
    from grokipedia_api.exceptions import (
        GrokipediaError,
        GrokipediaNotFoundError,
        GrokipediaAPIError,
        GrokipediaRateLimitError
    )
except ImportError:
    print("Error: grokipedia-api[async] is required.")
    print("Install with: pip install grokipedia-api[async]")
    sys.exit(1)


class GrokipediaScraper:
    """Scraper for all Grokipedia pages."""
    
    def __init__(
        self,
        output_dir: str = "grokipedia_scrape",
        max_workers: int = 50,
        batch_size: int = 100,
        rate_limit_delay: float = 0.1
    ):
        """Initialize the scraper.
        
        Args:
            output_dir: Directory to save scraped data
            max_workers: Maximum concurrent requests
            batch_size: Number of pages to fetch in each batch
            rate_limit_delay: Delay between requests in seconds
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.rate_limit_delay = rate_limit_delay
        
        # Progress tracking files
        self.slugs_file = self.output_dir / "discovered_slugs.txt"
        self.progress_file = self.output_dir / "scraping_progress.json"
        self.pages_dir = self.output_dir / "pages"
        self.pages_dir.mkdir(exist_ok=True)
        
        # State
        self.discovered_slugs: Set[str] = set()
        self.scraped_slugs: Set[str] = set()
        self.failed_slugs: Set[str] = set()
        self.stats = {
            "discovered": 0,
            "scraped": 0,
            "failed": 0,
            "start_time": None,
            "last_update": None
        }
        
        # Search queries for discovery
        self.search_queries = self._generate_search_queries()
        
        # Semaphore for rate limiting
        self.semaphore = asyncio.Semaphore(max_workers)
    
    def _generate_search_queries(self) -> List[str]:
        """Generate search queries to discover pages.
        
        Returns:
            List of search query strings
        """
        queries = []
        
        # Single letters (a-z)
        queries.extend([chr(i) for i in range(ord('a'), ord('z') + 1)])
        queries.extend([chr(i) for i in range(ord('A'), ord('Z') + 1)])
        
        # Numbers (0-9)
        queries.extend([str(i) for i in range(10)])
        
        # Common prefixes
        common_prefixes = [
            "the", "a", "an", "of", "in", "on", "at", "to", "for",
            "united", "new", "old", "great", "national", "international",
            "university", "college", "city", "state", "country", "world",
            "history", "science", "technology", "art", "music", "culture",
            "people", "person", "place", "thing", "event", "organization"
        ]
        queries.extend(common_prefixes)
        
        # Common words (2-4 letters)
        common_words = [
            "aa", "ab", "ac", "ad", "ae", "af", "ag", "ah", "ai", "aj",
            "ak", "al", "am", "an", "ao", "ap", "aq", "ar", "as", "at",
            "au", "av", "aw", "ax", "ay", "az",
            "ba", "be", "bi", "bo", "bu", "by",
            "ca", "ce", "ci", "co", "cu", "cy",
            "da", "de", "di", "do", "du", "dy",
            "ea", "eb", "ec", "ed", "ee", "ef", "eg", "eh", "ei", "ej",
            "ek", "el", "em", "en", "eo", "ep", "eq", "er", "es", "et",
            "eu", "ev", "ew", "ex", "ey", "ez",
            "fa", "fe", "fi", "fo", "fu", "fy",
            "ga", "ge", "gi", "go", "gu", "gy",
            "ha", "he", "hi", "ho", "hu", "hy",
            "ia", "ib", "ic", "id", "ie", "if", "ig", "ih", "ii", "ij",
            "ik", "il", "im", "in", "io", "ip", "iq", "ir", "is", "it",
            "iu", "iv", "iw", "ix", "iy", "iz",
            "ja", "je", "ji", "jo", "ju", "jy",
            "ka", "ke", "ki", "ko", "ku", "ky",
            "la", "le", "li", "lo", "lu", "ly",
            "ma", "me", "mi", "mo", "mu", "my",
            "na", "ne", "ni", "no", "nu", "ny",
            "oa", "ob", "oc", "od", "oe", "of", "og", "oh", "oi", "oj",
            "ok", "ol", "om", "on", "oo", "op", "oq", "or", "os", "ot",
            "ou", "ov", "ow", "ox", "oy", "oz",
            "pa", "pe", "pi", "po", "pu", "py",
            "qa", "qe", "qi", "qo", "qu", "qy",
            "ra", "re", "ri", "ro", "ru", "ry",
            "sa", "se", "si", "so", "su", "sy",
            "ta", "te", "ti", "to", "tu", "ty",
            "ua", "ub", "uc", "ud", "ue", "uf", "ug", "uh", "ui", "uj",
            "uk", "ul", "um", "un", "uo", "up", "uq", "ur", "us", "ut",
            "uu", "uv", "uw", "ux", "uy", "uz",
            "va", "ve", "vi", "vo", "vu", "vy",
            "wa", "we", "wi", "wo", "wu", "wy",
            "xa", "xe", "xi", "xo", "xu", "xy",
            "ya", "ye", "yi", "yo", "yu", "yy",
            "za", "ze", "zi", "zo", "zu", "zy"
        ]
        queries.extend(common_words)
        
        # Common 3-letter words
        queries.extend([
            "the", "and", "for", "are", "but", "not", "you", "all", "can",
            "her", "was", "one", "our", "out", "day", "get", "has", "him",
            "his", "how", "man", "new", "now", "old", "see", "two", "way",
            "who", "boy", "did", "its", "let", "put", "say", "she", "too",
            "use", "art", "act", "age", "air", "arm", "ask", "bag", "bar",
            "bat", "bed", "big", "bit", "box", "bus", "car", "cat", "cup",
            "cut", "dog", "dry", "eat", "egg", "end", "eye", "fan", "far",
            "fat", "few", "fig", "fin", "fit", "fix", "fly", "fog", "fox",
            "fun", "gap", "gas", "get", "gun", "guy", "had", "ham", "hat",
            "hay", "hen", "her", "hid", "him", "hip", "his", "hit", "hog",
            "hop", "hot", "how", "hub", "hug", "hum", "hut", "ice", "icy",
            "ill", "ink", "inn", "ion", "ire", "irk", "its", "jam", "jar",
            "jaw", "jay", "jet", "jig", "job", "jog", "jot", "joy", "jug",
            "jump", "junk", "jury", "just", "keen", "keep", "keg", "ken",
            "key", "kid", "kin", "kit", "lab", "lad", "lag", "lam", "lap",
            "law", "lax", "lay", "lea", "led", "lee", "leg", "let", "lid",
            "lie", "lip", "lit", "log", "lot", "low", "lox", "lug", "luk",
            "lump", "lurk", "lust", "lyn", "lye", "mad", "mag", "man",
            "map", "mar", "mat", "max", "may", "men", "met", "mid", "mix",
            "mob", "mod", "mom", "mon", "mop", "mot", "mow", "mud", "mug",
            "mum", "nab", "nag", "nap", "nay", "net", "new", "nib", "nil",
            "nip", "nit", "nod", "non", "nor", "not", "now", "nub", "nun",
            "nut", "oak", "oar", "oat", "odd", "ode", "off", "oft", "oil",
            "old", "ole", "one", "ooh", "opt", "orb", "orc", "ore", "org",
            "orn", "our", "out", "ova", "owe", "owl", "own", "oxo", "pac",
            "pad", "pah", "pal", "pan", "pap", "par", "pas", "pat", "paw",
            "pay", "pea", "peg", "pen", "pep", "per", "pet", "pew", "phi",
            "pie", "pig", "pin", "pip", "pit", "pix", "ply", "pod", "poe",
            "poi", "pol", "pop", "pot", "pow", "pox", "pro", "pry", "pub",
            "pug", "pun", "pup", "pur", "pus", "put", "pye", "pyx", "qat",
            "qed", "qis", "qua", "quo", "rad", "rag", "rah", "rai", "raj",
            "ram", "ran", "rap", "rat", "raw", "ray", "reb", "rec", "red",
            "ree", "ref", "reg", "rei", "rem", "ren", "rep", "res", "ret",
            "rev", "rex", "rho", "rib", "rid", "rif", "rig", "rim", "rin",
            "rip", "rob", "roc", "rod", "roe", "rog", "rom", "rot", "row",
            "rub", "rue", "rug", "rum", "run", "rut", "rye", "sab", "sac",
            "sad", "sae", "sag", "sai", "sal", "sam", "san", "sap", "sat",
            "sau", "saw", "sax", "say", "sea", "sec", "see", "seg", "sei",
            "sel", "sen", "ser", "set", "sew", "sex", "she", "shy", "sib",
            "sic", "sim", "sin", "sip", "sir", "sis", "sit", "six", "ska",
            "ski", "sky", "sly", "sob", "sod", "sol", "som", "son", "sop",
            "sot", "sou", "sow", "sox", "soy", "spa", "spy", "sty", "sub",
            "sue", "sum", "sun", "sup", "suq", "sur", "sus", "swy", "tab",
            "tad", "tae", "tag", "tai", "taj", "tak", "tal", "tam", "tan",
            "tao", "tap", "tar", "tas", "tat", "tau", "tav", "taw", "tax",
            "tay", "tea", "tec", "ted", "tee", "teg", "tel", "tem", "ten",
            "ter", "tes", "tet", "tew", "tex", "the", "tho", "thy", "tic",
            "tie", "tig", "til", "tim", "tin", "tip", "tis", "tit", "tod",
            "toe", "tog", "tom", "ton", "too", "top", "tor", "tot", "tow",
            "toy", "try", "tsk", "tub", "tug", "tui", "tum", "tun", "tup",
            "tut", "tux", "twa", "two", "twp", "tye", "tyg", "udo", "ugh",
            "uke", "ulu", "umm", "ump", "ums", "uni", "uns", "upo", "ups",
            "urb", "urd", "ure", "urg", "urn", "urp", "use", "uta", "ute",
            "uts", "vac", "van", "var", "vas", "vat", "vau", "vav", "vaw",
            "vee", "veg", "vet", "vex", "via", "vid", "vie", "vig", "vim",
            "vin", "vis", "voe", "vog", "vow", "vox", "vug", "vum", "wab",
            "wad", "wae", "wag", "wah", "wan", "wap", "war", "was", "wat",
            "waw", "wax", "way", "web", "wed", "wee", "wen", "wet", "wha",
            "who", "why", "wig", "win", "wis", "wit", "wiz", "woe", "wog",
            "wok", "won", "woo", "wop", "wot", "wow", "wry", "wud", "wye",
            "wyo", "xed", "xis", "yag", "yah", "yak", "yam", "yap", "yar",
            "yaw", "yay", "yea", "yeh", "yen", "yep", "yes", "yet", "yew",
            "yid", "yin", "yip", "yob", "yod", "yok", "yom", "yon", "you",
            "yow", "yoy", "yuk", "yum", "yup", "yus", "zag", "zap", "zas",
            "zax", "zed", "zee", "zek", "zen", "zep", "zes", "zex", "zig",
            "zin", "zip", "zit", "zoa", "zoo", "zoo", "zos", "zuz", "zzz"
        ])
        
        return queries
    
    def load_progress(self):
        """Load previous scraping progress."""
        # Load discovered slugs
        if self.slugs_file.exists():
            with open(self.slugs_file, 'r') as f:
                self.discovered_slugs = set(line.strip() for line in f if line.strip())
        
        # Load progress stats
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.stats = json.load(f)
        
        # Load already scraped slugs
        if self.pages_dir.exists():
            for file in self.pages_dir.glob("*.json"):
                slug = file.stem
                self.scraped_slugs.add(slug)
        
        print(f"Loaded progress: {len(self.discovered_slugs)} discovered, "
              f"{len(self.scraped_slugs)} scraped")
    
    def save_progress(self):
        """Save current scraping progress."""
        # Save discovered slugs
        with open(self.slugs_file, 'w') as f:
            for slug in sorted(self.discovered_slugs):
                f.write(f"{slug}\n")
        
        # Update and save stats
        self.stats["discovered"] = len(self.discovered_slugs)
        self.stats["scraped"] = len(self.scraped_slugs)
        self.stats["failed"] = len(self.failed_slugs)
        self.stats["last_update"] = datetime.now().isoformat()
        
        with open(self.progress_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    async def discover_slugs_from_search(
        self,
        client: AsyncGrokipediaClient,
        query: str,
        limit: int = 100
    ) -> Set[str]:
        """Discover page slugs from a search query.
        
        Args:
            client: Async client instance
            query: Search query
            limit: Results per page
            
        Returns:
            Set of discovered slugs
        """
        discovered = set()
        offset = 0
        
        while True:
            try:
                async with self.semaphore:
                    await asyncio.sleep(self.rate_limit_delay)
                    results = await client.search(query, limit=limit, offset=offset)
                
                slugs = {r.get("slug") for r in results.get("results", []) if r.get("slug")}
                if not slugs:
                    break
                
                discovered.update(slugs)
                offset += limit
                
                # Check if we got fewer results than requested (end of results)
                if len(results.get("results", [])) < limit:
                    break
                    
            except GrokipediaRateLimitError:
                print(f"Rate limited, waiting 5 seconds...")
                await asyncio.sleep(5)
                continue
            except Exception as e:
                print(f"Error searching '{query}': {e}")
                break
        
        return discovered
    
    async def discover_all_slugs(self):
        """Discover all page slugs using search queries."""
        print(f"Starting discovery phase with {len(self.search_queries)} queries...")
        self.stats["start_time"] = datetime.now().isoformat()
        
        async with AsyncGrokipediaClient() as client:
            tasks = []
            for query in self.search_queries:
                task = self.discover_slugs_from_search(client, query)
                tasks.append(task)
            
            # Process in batches to avoid overwhelming the API
            batch_size = 10
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, set):
                        new_slugs = result - self.discovered_slugs
                        self.discovered_slugs.update(new_slugs)
                        if new_slugs:
                            print(f"Discovered {len(new_slugs)} new slugs "
                                  f"(total: {len(self.discovered_slugs)})")
                
                # Save progress periodically
                self.save_progress()
                
                # Small delay between batches
                await asyncio.sleep(1)
        
        print(f"Discovery complete: {len(self.discovered_slugs)} unique slugs found")
        self.save_progress()
    
    async def scrape_page(
        self,
        client: AsyncGrokipediaClient,
        slug: str
    ) -> Optional[Dict[str, Any]]:
        """Scrape a single page.
        
        Args:
            client: Async client instance
            slug: Page slug
            
        Returns:
            Page data or None if failed
        """
        try:
            async with self.semaphore:
                await asyncio.sleep(self.rate_limit_delay)
                page_data = await client.get_page(slug, include_content=True)
            
            return page_data
        except GrokipediaNotFoundError:
            self.failed_slugs.add(slug)
            return None
        except GrokipediaRateLimitError:
            print(f"Rate limited, waiting 5 seconds...")
            await asyncio.sleep(5)
            # Retry once
            try:
                async with self.semaphore:
                    await asyncio.sleep(self.rate_limit_delay)
                    page_data = await client.get_page(slug, include_content=True)
                return page_data
            except Exception:
                self.failed_slugs.add(slug)
                return None
        except Exception as e:
            print(f"Error scraping {slug}: {e}")
            self.failed_slugs.add(slug)
            return None
    
    async def scrape_all_pages(self):
        """Scrape all discovered pages."""
        slugs_to_scrape = self.discovered_slugs - self.scraped_slugs
        
        if not slugs_to_scrape:
            print("No pages to scrape!")
            return
        
        print(f"Starting scraping phase: {len(slugs_to_scrape)} pages to scrape...")
        
        slugs_list = list(slugs_to_scrape)
        total = len(slugs_list)
        
        async with AsyncGrokipediaClient() as client:
            for i in range(0, total, self.batch_size):
                batch = slugs_list[i:i + self.batch_size]
                
                tasks = [self.scrape_page(client, slug) for slug in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for slug, page_data in zip(batch, results):
                    if isinstance(page_data, dict) and page_data.get("found"):
                        # Save page
                        page_file = self.pages_dir / f"{slug}.json"
                        with open(page_file, 'w') as f:
                            json.dump(page_data, f, indent=2)
                        
                        self.scraped_slugs.add(slug)
                    
                    # Progress update
                    if (i + len(batch)) % 100 == 0:
                        progress = len(self.scraped_slugs)
                        print(f"Progress: {progress}/{total} pages scraped "
                              f"({100 * progress / total:.1f}%)")
                        self.save_progress()
                
                # Save progress after each batch
                self.save_progress()
        
        print(f"Scraping complete: {len(self.scraped_slugs)} pages scraped, "
              f"{len(self.failed_slugs)} failed")
    
    async def run(self, resume: bool = False):
        """Run the full scraping process.
        
        Args:
            resume: If True, resume from previous progress
        """
        if resume:
            self.load_progress()
        
        # Discovery phase
        if len(self.discovered_slugs) < 1000:  # Re-discover if we have too few
            await self.discover_all_slugs()
        else:
            print(f"Using {len(self.discovered_slugs)} previously discovered slugs")
        
        # Scraping phase
        await self.scrape_all_pages()
        
        # Final save
        self.save_progress()
        
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        print(f"Total discovered: {len(self.discovered_slugs)}")
        print(f"Total scraped: {len(self.scraped_slugs)}")
        print(f"Total failed: {len(self.failed_slugs)}")
        print(f"Output directory: {self.output_dir}")
        print("="*60)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape all pages from Grokipedia (~1M pages)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="grokipedia_scrape",
        help="Directory to save scraped data (default: grokipedia_scrape)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous scraping progress"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=50,
        help="Maximum concurrent requests (default: 50)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for scraping (default: 100)"
    )
    parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=0.1,
        help="Delay between requests in seconds (default: 0.1)"
    )
    
    args = parser.parse_args()
    
    scraper = GrokipediaScraper(
        output_dir=args.output_dir,
        max_workers=args.max_workers,
        batch_size=args.batch_size,
        rate_limit_delay=args.rate_limit_delay
    )
    
    await scraper.run(resume=args.resume)


if __name__ == "__main__":
    asyncio.run(main())

