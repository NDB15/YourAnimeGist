#!/usr/bin/env python3
"""
Update all anime in anime_data.json with English titles from Jikan API

This script:
1. Reads all anime from anime_data.json
2. For each anime, fetches English title from Jikan API
3. Updates the anime_data.json with proper title_english field
4. Saves progress incrementally every 100 anime

Usage:
    python3 update_english_titles.py [start_index] [end_index]
    
Examples:
    python3 update_english_titles.py           # Update all anime
    python3 update_english_titles.py 0 1000    # Update first 1000
    python3 update_english_titles.py 1000 2000 # Resume from 1000
"""

import json
import requests
import time
import sys
from datetime import datetime

ANIME_FILE = 'anime_data.json'
JIKAN_API = 'https://api.jikan.moe/v4/anime/'
DELAY = 0.5  # Jikan rate limit: 3 requests/second, so 0.33s minimum
BATCH_SIZE = 100

def fetch_english_title(mal_id):
    """Fetch English title from Jikan API"""
    try:
        response = requests.get(f"{JIKAN_API}{mal_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Get English title from the data
            title_english = data.get('data', {}).get('title_english')
            title = data.get('data', {}).get('title')  # Japanese title
            return title_english if title_english else title
        elif response.status_code == 429:
            print(f"  Rate limited, waiting 5 seconds...")
            time.sleep(5)
            return fetch_english_title(mal_id)
        else:
            return None
    except Exception as e:
        print(f"  Error fetching MAL ID {mal_id}: {e}")
        return None

def update_english_titles(start_idx=0, end_idx=None):
    """Update English titles for anime in range"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading anime data...")
    
    with open(ANIME_FILE, 'r', encoding='utf-8') as f:
        anime_data = json.load(f)
    
    total = len(anime_data)
    end_idx = end_idx if end_idx else total
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Total anime: {total}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating range: {start_idx} to {end_idx}")
    print()
    
    updated = 0
    failed = 0
    skipped = 0
    
    for idx in range(start_idx, min(end_idx, total)):
        anime = anime_data[idx]
        mal_id = anime.get('mal_id')
        current_english = anime.get('title_english')
        
        # Skip if already has English title different from Japanese
        if current_english and current_english != anime.get('title'):
            skipped += 1
            continue
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{idx+1}/{total}] Fetching: {anime.get('title')}")
        
        title_english = fetch_english_title(mal_id)
        
        if title_english:
            anime['title_english'] = title_english
            updated += 1
            print(f"  ✓ English: {title_english}")
        else:
            failed += 1
            print(f"  ✗ Failed to fetch")
        
        # Save progress every BATCH_SIZE anime
        if (idx + 1) % BATCH_SIZE == 0:
            with open(ANIME_FILE, 'w', encoding='utf-8') as f:
                json.dump(anime_data, f, ensure_ascii=False)
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Progress saved! Updated: {updated}, Failed: {failed}, Skipped: {skipped}\n")
        
        time.sleep(DELAY)
    
    # Final save
    with open(ANIME_FILE, 'w', encoding='utf-8') as f:
        json.dump(anime_data, f, ensure_ascii=False)
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✓ Complete!")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Updated: {updated}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed: {failed}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Skipped: {skipped}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Updated file: {ANIME_FILE}")

if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    update_english_titles(start, end)
