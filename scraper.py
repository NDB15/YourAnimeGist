"""
MyAnimeList API Fetcher using Jikan API
Fetches anime data including titles, ratings, and genres INSTANTLY
"""

import requests
import json
import time
from typing import List, Dict

class MALScraper:
    def __init__(self):
        self.base_url = "https://api.jikan.moe/v4"
        self.anime_data = []
        
    def scrape_top_anime(self, limit=None, incremental=False):
        """Fetch anime from Jikan API
        
        Args:
            limit: Maximum number of anime to fetch (None = all)
            incremental: If True, only fetch anime newer than existing data
        """
        start_mal_id = 1
        
        # Clear existing data on full refresh to prevent duplicates
        if not incremental:
            self.anime_data = []
        
        if incremental and self.anime_data:
            # Get highest MAL ID from existing data
            start_mal_id = max(a['mal_id'] for a in self.anime_data if a.get('mal_id')) + 1
            print(f"🔄 Incremental update: Fetching anime starting from MAL ID {start_mal_id}...")
        elif limit:
            print(f"Fetching {limit} anime from Jikan API...")
        else:
            print("Fetching ALL anime from Jikan API (this will take several minutes)...")
        
        page = 1
        per_page = 25  # Jikan API limit
        new_anime_count = 0
        
        while limit is None or len(self.anime_data) < limit:
            # Use /anime endpoint to get ALL anime, not just top-rated
            url = f"{self.base_url}/anime?page={page}&limit={per_page}&order_by=mal_id&sort=asc"
            
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                data = response.json()
                anime_list = data.get('data', [])
                
                if not anime_list:
                    break
                
                for anime in anime_list:
                    mal_id = anime.get('mal_id')
                    
                    # Skip anime below start_mal_id in incremental mode
                    if incremental and mal_id and mal_id < start_mal_id:
                        continue
                    
                    if limit is not None and len(self.anime_data) >= limit:
                        break
                    
                    # Extract genres
                    genres = [g['name'] for g in anime.get('genres', [])]
                    
                    # Extract year from aired data
                    year = None
                    if anime.get('aired') and anime['aired'].get('prop') and anime['aired']['prop'].get('from'):
                        year = anime['aired']['prop']['from'].get('year')
                    elif anime.get('year'):
                        year = anime.get('year')
                    
                    # Extract image URL
                    image_url = ''
                    if anime.get('images') and anime['images'].get('jpg'):
                        image_url = anime['images']['jpg'].get('large_image_url') or anime['images']['jpg'].get('image_url', '')
                    
                    anime_info = {
                        'title': anime.get('title', 'Unknown'),
                        'rating': anime.get('score', 0.0) or 0.0,
                        'type': anime.get('type', 'Unknown'),
                        'episodes': f"{anime.get('episodes', '?')} eps" if anime.get('episodes') else 'Unknown',
                        'url': anime.get('url', ''),
                        'genres': genres,
                        'mal_id': anime.get('mal_id'),
                        'year': year,
                        'image_url': image_url
                    }
                    
                    # Check for duplicates by mal_id
                    existing_anime = None
                    if mal_id:
                        existing_anime = next((a for a in self.anime_data if a.get('mal_id') == mal_id), None)
                    
                    if existing_anime:
                        # Update existing entry with latest data (e.g., updated ratings)
                        existing_anime.update(anime_info)
                        print(f"Updated: {anime_info['title']} (Rating: {anime_info['rating']})")
                    else:
                        # Add new anime
                        self.anime_data.append(anime_info)
                        new_anime_count += 1
                        print(f"Fetched: {anime_info['title']} (Rating: {anime_info['rating']})")
                
                # In incremental mode, if we got no new anime this page, we're done
                if incremental and new_anime_count == 0:
                    print(f"✅ No new anime found - database is up to date")
                    break
                
                page += 1
                time.sleep(1)  # Longer delay for API rate limiting (was 0.5)
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                # If rate limited, wait longer and retry
                if "429" in str(e) or "Too Many Requests" in str(e):
                    print(f"Rate limited. Waiting 10 seconds before continuing...")
                    time.sleep(10)
                    continue
                break
        
        print(f"Successfully fetched {len(self.anime_data)} anime in seconds!")
        return self.anime_data
    
    def patch_missing_fields(self, batch_size=500, max_batches=None):
        """Patch anime that are missing year or image_url data
        
        Args:
            batch_size: Number of anime to patch per run
            max_batches: Maximum batches to process (None = all)
        """
        print("🔧 Checking for anime with missing year or image data...")
        
        # Find anime missing year or image_url
        needs_patch = [
            anime for anime in self.anime_data 
            if not anime.get('year') or not anime.get('image_url')
        ]
        
        if not needs_patch:
            print("✅ All anime have complete data!")
            return 0
        
        total_to_patch = min(len(needs_patch), batch_size * (max_batches or float('inf')))
        print(f"📊 Found {len(needs_patch)} anime with missing data")
        print(f"🔄 Will patch {total_to_patch} anime this run...")
        
        patched_count = 0
        for i, anime in enumerate(needs_patch[:total_to_patch]):
            if not anime.get('mal_id'):
                continue
            
            try:
                # Fetch individual anime data
                url = f"{self.base_url}/anime/{anime['mal_id']}"
                response = requests.get(url)
                response.raise_for_status()
                
                api_data = response.json()['data']
                
                # Patch year if missing
                if not anime.get('year'):
                    year = None
                    if api_data.get('aired') and api_data['aired'].get('prop') and api_data['aired']['prop'].get('from'):
                        year = api_data['aired']['prop']['from'].get('year')
                    elif api_data.get('year'):
                        year = api_data.get('year')
                    if year:
                        anime['year'] = year
                
                # Patch image_url if missing
                if not anime.get('image_url'):
                    if api_data.get('images') and api_data['images'].get('jpg'):
                        image_url = api_data['images']['jpg'].get('large_image_url') or api_data['images']['jpg'].get('image_url', '')
                        if image_url:
                            anime['image_url'] = image_url
                
                patched_count += 1
                if patched_count % 50 == 0:
                    print(f"  Patched {patched_count}/{total_to_patch} anime...")
                
                # Slower rate limiting for individual requests
                time.sleep(0.5)
                
            except Exception as e:
                if "429" in str(e):
                    print(f"  Rate limited at {patched_count}/{total_to_patch}, waiting 10 seconds...")
                    time.sleep(10)
                    continue
                print(f"  ⚠️ Error patching {anime['title']}: {e}")
                continue
        
        print(f"✅ Patched {patched_count} anime with missing data")
        return patched_count
    
    def enrich_with_genres(self, limit=50):
        """Genres are already included from Jikan API - no additional work needed!"""
        print("✅ All anime already have genre data from Jikan API!")
    
    def save_to_json(self, filename='anime_data.json'):
        """Save scraped data to JSON file (atomic write using temp file)"""
        import os
        temp_filename = filename + '.tmp'
        
        # Write to temp file first
        with open(temp_filename, 'w', encoding='utf-8') as f:
            json.dump(self.anime_data, f, indent=2, ensure_ascii=False)
        
        # Only replace main file when write is complete
        os.replace(temp_filename, filename)
        print(f"Data saved to {filename}")
    
    def load_from_json(self, filename='anime_data.json'):
        """Load data from JSON file and remove duplicates"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content == '[]' or content == '{}':
                    print(f"File {filename} exists but is empty or invalid")
                    return []
                loaded_data = json.loads(content)
            
            # Deduplicate by mal_id (keep the last occurrence which is usually most recent)
            seen_ids = {}
            for anime in loaded_data:
                mal_id = anime.get('mal_id')
                if mal_id:
                    seen_ids[mal_id] = anime
                else:
                    # For anime without mal_id, use title as fallback
                    title = anime.get('title', '')
                    if title:
                        seen_ids[f"title_{title}"] = anime
            
            self.anime_data = list(seen_ids.values())
            
            duplicates_removed = len(loaded_data) - len(self.anime_data)
            if duplicates_removed > 0:
                print(f"🔧 Removed {duplicates_removed} duplicate entries")
            
            print(f"Loaded {len(self.anime_data)} anime from {filename}")
            return self.anime_data
        except FileNotFoundError:
            print(f"File {filename} not found")
            return []
        except json.JSONDecodeError:
            print(f"File {filename} contains invalid JSON")
            return []

def main():
    """Main function to fetch anime data"""
    import sys
    import os
    from datetime import datetime
    
    scraper = MALScraper()
    
    # Check existing data count
    existing_data = scraper.load_from_json()
    existing_count = len(existing_data)
    MIN_ANIME_COUNT = 28000
    
    # Check if we should do a full refresh (weekly on Sundays or if FORCE_FULL_REFRESH is set)
    force_full = os.environ.get('FORCE_FULL_REFRESH', '').lower() == 'true'
    is_sunday = datetime.utcnow().weekday() == 6  # Sunday = 6
    should_full_refresh = force_full or is_sunday
    
    # If count is below threshold, always do full refresh
    if existing_count < MIN_ANIME_COUNT:
        print(f"📊 Only {existing_count} anime (< {MIN_ANIME_COUNT}). Doing full refresh...")
        should_full_refresh = True
    
    if should_full_refresh:
        # Full refresh: Fetch everything to update ratings
        print(f"🔄 Full refresh: Fetching all anime to update ratings and add new entries...")
        scraper.scrape_top_anime()  # No limit - fetch ALL anime
        
        # Only save if we got enough data
        if len(scraper.anime_data) < MIN_ANIME_COUNT:
            print(f"⚠️  Only fetched {len(scraper.anime_data)} anime (< {MIN_ANIME_COUNT}). NOT saving to avoid incomplete data.")
            sys.exit(1)
    else:
        # Incremental update: Only fetch new anime
        print(f"⚡ Incremental update: Checking for new anime (current: {existing_count})...")
        scraper.anime_data = existing_data  # Start with existing data
        old_count = len(scraper.anime_data)
        
        scraper.scrape_top_anime(incremental=True)  # Only fetch new anime
        
        new_count = len(scraper.anime_data) - old_count
        if new_count > 0:
            print(f"✨ Found {new_count} new anime!")
        else:
            print(f"✅ No new anime found")
        
        # Also patch missing year/image data in batches
        print(f"\n🔧 Checking for missing year/image data...")
        patched = scraper.patch_missing_fields(batch_size=500, max_batches=1)
        
        if new_count == 0 and patched == 0:
            print(f"✅ Database is fully up to date - no changes needed")
            return  # No need to save if nothing changed
    
    scraper.save_to_json()
    print("✅ Done!")
    
    # Print summary
    if scraper.anime_data:
        print(f"\n📊 Total anime: {len(scraper.anime_data)}")
        print(f"📺 Sample: {scraper.anime_data[0]['title']} - Rating: {scraper.anime_data[0]['rating']}")
        
        # Get all unique genres
        all_genres = set()
        for anime in scraper.anime_data:
            all_genres.update(anime.get('genres', []))
        print(f"🎭 Unique genres found ({len(all_genres)}): {sorted(all_genres)}")

if __name__ == "__main__":
    main()
