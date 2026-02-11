#!/usr/bin/env python3
"""
Retry fetching English titles for anime that failed due to network errors only.
Does NOT retry anime that legitimately don't have English titles.
"""

import json
import re
import requests
import time
from datetime import datetime
from difflib import SequenceMatcher

ANIME_FILE = 'anime_data.json'
CACHE_FILE = 'seriesgraph_cache.json'
LOG_FILE = 'match_all.log'
JIKAN_API = 'https://api.jikan.moe/v4/anime/'
DELAY = 0.5
MATCH_THRESHOLD = 0.80

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_failed_mal_ids():
    """Extract MAL IDs that failed due to network errors from log"""
    failed_ids = set()
    
    with open(LOG_FILE, 'r') as f:
        for line in f:
            # Look for actual network error messages
            if 'Error fetching MAL ID' in line:
                match = re.search(r'MAL ID (\d+):', line)
                if match:
                    failed_ids.add(int(match.group(1)))
    
    return sorted(list(failed_ids))

def fetch_english_title(mal_id):
    """Fetch English title from Jikan API"""
    try:
        response = requests.get(f"{JIKAN_API}{mal_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('title_english')
        elif response.status_code == 429:
            print(f"  Rate limited, waiting 5 seconds...")
            time.sleep(5)
            return fetch_english_title(mal_id)
        else:
            return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def retry_failed_anime():
    """Retry fetching only anime that failed due to network errors"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading data...")
    
    # Load anime data
    with open(ANIME_FILE, 'r', encoding='utf-8') as f:
        anime_data = json.load(f)
    
    # Load SeriesGraph cache
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        sg_cache = json.load(f)
        sg_shows = sg_cache['shows']
    
    # Extract failed MAL IDs from log
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Extracting failed MAL IDs from log...")
    failed_ids = extract_failed_mal_ids()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(failed_ids)} anime with network errors")
    print()
    
    if len(failed_ids) == 0:
        print("No network errors found. All anime processed successfully!")
        return
    
    # Create lookup dict for quick access
    anime_by_id = {a.get('mal_id'): a for a in anime_data if a.get('mal_id')}
    
    updated_titles = 0
    updated_sg = 0
    still_failed = 0
    
    for idx, mal_id in enumerate(failed_ids):
        anime = anime_by_id.get(mal_id)
        if not anime:
            continue
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{idx+1}/{len(failed_ids)}] Retrying: {anime.get('title')}")
        
        # Try to fetch English title
        english_title = fetch_english_title(mal_id)
        
        if english_title:
            anime['title_english'] = english_title
            updated_titles += 1
            print(f"  ✓ English: {english_title}")
            
            # Try SeriesGraph matching with new English title
            if not anime.get('seriesgraph_url'):
                titles_to_check = [anime.get('title'), english_title]
                
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
                
                if best_score >= MATCH_THRESHOLD and best_match:
                    anime['seriesgraph_url'] = best_match['url']
                    updated_sg += 1
                    print(f"  ✓ SeriesGraph: {best_match['title']} (score: {best_score:.2f})")
        else:
            still_failed += 1
            print(f"  ✗ Still failed to fetch")
        
        time.sleep(DELAY)
        
        # Save every 50 anime
        if (idx + 1) % 50 == 0:
            with open(ANIME_FILE, 'w', encoding='utf-8') as f:
                json.dump(anime_data, f, ensure_ascii=False)
            print(f"\n  Progress saved! ({idx+1}/{len(failed_ids)})\n")
    
    # Final save
    with open(ANIME_FILE, 'w', encoding='utf-8') as f:
        json.dump(anime_data, f, ensure_ascii=False)
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✓ Retry complete!")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] English titles fetched: {updated_titles}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] SeriesGraph matched: {updated_sg}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Still failed: {still_failed}")

if __name__ == '__main__':
    retry_failed_anime()
