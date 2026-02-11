#!/usr/bin/env python3
"""
SeriesGraph Database Scraper and Matcher

This script:
1. Scrapes all shows from SeriesGraph into a local cache
2. Matches anime from anime_data.json against the SeriesGraph database
3. Updates anime_data.json with seriesgraph_url fields

Usage:
    python3 scrape_seriesgraph.py --scrape    # Scrape SeriesGraph (run once)
    python3 scrape_seriesgraph.py --match     # Match anime to SeriesGraph
    python3 scrape_seriesgraph.py --full      # Do both (scrape then match)
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import argparse
from difflib import SequenceMatcher

CACHE_FILE = 'seriesgraph_cache.json'
ANIME_FILE = 'anime_data.json'
BASE_URL = 'https://seriesgraph.com'
DELAY = 2  # seconds between requests

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def scrape_all_seriesgraph_shows():
    """Scrape all shows from SeriesGraph and save to cache"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting SeriesGraph scraper...")
    
    all_shows = []
    page = 1
    total_shows = 0
    
    while True:
        url = f"{BASE_URL}/all-shows/{page}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scraping page {page}...")
        
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }, timeout=30)
            
            if response.status_code != 200:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Page {page} returned status {response.status_code}, stopping.")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all show links
            show_links = soup.find_all('a', href=lambda x: x and '/show/' in x)
            
            if not show_links:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No shows found on page {page}, stopping.")
                break
            
            page_shows = []
            for link in show_links:
                href = link.get('href', '')
                if '/show/' in href:
                    # Extract show ID and slug from URL
                    # Format: /show/{id}-{slug}
                    parts = href.replace('/show/', '').split('-', 1)
                    if len(parts) == 2:
                        show_id = parts[0]
                        slug = parts[1]
                        
                        # Convert slug to full title (slugs have complete titles)
                        # e.g., "frieren-beyond-journeys-end" -> "Frieren Beyond Journeys End"
                        title = slug.replace('-', ' ').title()
                        
                        show_data = {
                            'id': show_id,
                            'slug': slug,
                            'title': title,
                            'url': f"{BASE_URL}{href}"
                        }
                        
                        # Avoid duplicates
                        if not any(s['id'] == show_id for s in page_shows):
                            page_shows.append(show_data)
            
            all_shows.extend(page_shows)
            total_shows = len(all_shows)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(page_shows)} shows on page {page} (Total: {total_shows})")
            
            # Check if we should continue
            if len(page_shows) == 0:
                break
            
            page += 1
            time.sleep(DELAY)
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error on page {page}: {e}")
            break
    
    # Save to cache
    cache_data = {
        'scraped_at': datetime.now().isoformat(),
        'total_shows': len(all_shows),
        'shows': all_shows
    }
    
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✓ Scraping complete!")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Total shows scraped: {len(all_shows)}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Cache saved to: {CACHE_FILE}")
    
    return all_shows

def load_seriesgraph_cache():
    """Load SeriesGraph cache from file"""
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded cache with {cache['total_shows']} shows")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Cache created: {cache['scraped_at']}")
            return cache['shows']
    except FileNotFoundError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: Cache file not found. Run with --scrape first.")
        return None

def match_anime_to_seriesgraph(threshold=0.85):
    """Match anime to SeriesGraph shows and update anime_data.json"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting anime matching...")
    
    # Load SeriesGraph cache
    sg_shows = load_seriesgraph_cache()
    if not sg_shows:
        return
    
    # Load anime data
    with open(ANIME_FILE, 'r', encoding='utf-8') as f:
        anime_data = json.load(f)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded {len(anime_data)} anime")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Matching with threshold: {threshold}")
    
    matched = 0
    not_matched = 0
    batch_size = 1000
    
    for idx, anime in enumerate(anime_data):
        # Try matching with both title and title_english
        titles_to_check = [anime.get('title', '')]
        if anime.get('title_english'):
            titles_to_check.append(anime['title_english'])
        
        best_match = None
        best_score = 0
        
        for title in titles_to_check:
            if not title:
                continue
            
            for show in sg_shows:
                score = similarity(title, show['title'])
                if score > best_score:
                    best_score = score
                    best_match = show
        
        # If match is above threshold, add URL
        if best_score >= threshold and best_match:
            anime['seriesgraph_url'] = best_match['url']
            matched += 1
        else:
            not_matched += 1
        
        # Progress update every batch
        if (idx + 1) % batch_size == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Progress: {idx + 1}/{len(anime_data)} | Matched: {matched} | Not matched: {not_matched}")
            
            # Save incrementally
            with open(ANIME_FILE, 'w', encoding='utf-8') as f:
                json.dump(anime_data, f, ensure_ascii=False)
    
    # Final save
    with open(ANIME_FILE, 'w', encoding='utf-8') as f:
        json.dump(anime_data, f, ensure_ascii=False)
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✓ Matching complete!")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Matched: {matched}/{len(anime_data)} ({matched/len(anime_data)*100:.1f}%)")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Not matched: {not_matched}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Updated: {ANIME_FILE}")

def main():
    parser = argparse.ArgumentParser(description='SeriesGraph scraper and matcher')
    parser.add_argument('--scrape', action='store_true', help='Scrape all SeriesGraph shows')
    parser.add_argument('--match', action='store_true', help='Match anime to SeriesGraph')
    parser.add_argument('--full', action='store_true', help='Scrape then match')
    parser.add_argument('--threshold', type=float, default=0.85, help='Matching threshold (default: 0.85)')
    
    args = parser.parse_args()
    
    if args.full:
        scrape_all_seriesgraph_shows()
        match_anime_to_seriesgraph(args.threshold)
    elif args.scrape:
        scrape_all_seriesgraph_shows()
    elif args.match:
        match_anime_to_seriesgraph(args.threshold)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
