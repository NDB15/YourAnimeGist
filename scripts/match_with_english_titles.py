#!/usr/bin/env python3
"""
Enhanced matcher that:
1. Fetches English titles from Jikan API for all anime
2. Matches both Japanese and English titles against SeriesGraph cache
3. Updates anime_data.json with both title_english and seriesgraph_url

This is much faster than the original approach since we already have
the SeriesGraph database cached!
"""

import json
import requests
import time
from datetime import datetime
from difflib import SequenceMatcher
import sys

ANIME_FILE = 'anime_data.json'
CACHE_FILE = 'seriesgraph_cache.json'
JIKAN_API = 'https://api.jikan.moe/v4/anime/'
DELAY = 0.5  # Jikan rate limit
BATCH_SIZE = 100
MATCH_THRESHOLD = 0.80  # Lowered because SeriesGraph titles are sometimes truncated

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

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
        print(f"  Error fetching MAL ID {mal_id}: {e}")
        return None

def match_anime_with_english_titles(start_idx=0, end_idx=None):
    """Fetch English titles and match with SeriesGraph in one pass"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading data...")
    
    # Load anime data
    with open(ANIME_FILE, 'r', encoding='utf-8') as f:
        anime_data = json.load(f)
    
    # Load SeriesGraph cache
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        sg_cache = json.load(f)
        sg_shows = sg_cache['shows']
    
    total = len(anime_data)
    end_idx = end_idx if end_idx else total
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Total anime: {total:,}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] SeriesGraph shows: {len(sg_shows):,}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing range: {start_idx} to {end_idx}")
    print()
    
    updated_titles = 0
    updated_sg = 0
    failed = 0
    skipped = 0
    
    for idx in range(start_idx, min(end_idx, total)):
        anime = anime_data[idx]
        mal_id = anime.get('mal_id')
        japanese_title = anime.get('title')
        current_english = anime.get('title_english')
        
        # Skip if already has both English title and SeriesGraph URL
        if current_english and anime.get('seriesgraph_url'):
            skipped += 1
            if (idx + 1) % 1000 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{idx+1}/{total}] Skipped {skipped} already complete")
            continue
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{idx+1}/{total}] {japanese_title}")
        
        # Fetch English title if missing
        english_title = current_english
        if not english_title:
            english_title = fetch_english_title(mal_id)
            if english_title:
                anime['title_english'] = english_title
                updated_titles += 1
                print(f"  ✓ English: {english_title}")
            else:
                failed += 1
                print(f"  ✗ Failed to fetch English title")
            time.sleep(DELAY)
        else:
            print(f"  • English: {english_title}")
        
        # Match with SeriesGraph using both titles
        if not anime.get('seriesgraph_url'):
            titles_to_check = [japanese_title]
            if english_title and english_title != japanese_title:
                titles_to_check.append(english_title)
            
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
                print(f"  - No SeriesGraph match (best: {best_score:.2f})")
        else:
            print(f"  • SeriesGraph: Already set")
        
        # Save progress every BATCH_SIZE anime
        if (idx + 1) % BATCH_SIZE == 0:
            with open(ANIME_FILE, 'w', encoding='utf-8') as f:
                json.dump(anime_data, f, ensure_ascii=False)
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Progress saved!")
            print(f"  Titles updated: {updated_titles}, SG matched: {updated_sg}, Failed: {failed}, Skipped: {skipped}\n")
    
    # Final save
    with open(ANIME_FILE, 'w', encoding='utf-8') as f:
        json.dump(anime_data, f, ensure_ascii=False)
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✓ Complete!")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] English titles updated: {updated_titles}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] SeriesGraph matched: {updated_sg}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed: {failed}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Skipped: {skipped}")

if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    match_anime_with_english_titles(start, end)
