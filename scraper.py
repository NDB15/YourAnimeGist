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
        
    def scrape_top_anime(self, limit=None):
        """Fetch ALL anime from Jikan API (or up to limit if specified)"""
        if limit:
            print(f"Fetching {limit} anime from Jikan API...")
        else:
            print("Fetching ALL anime from Jikan API (this will take several minutes)...")
        
        page = 1
        per_page = 25  # Jikan API limit
        
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
                    if limit is not None and len(self.anime_data) >= limit:
                        break
                    
                    # Extract genres
                    genres = [g['name'] for g in anime.get('genres', [])]
                    
                    anime_info = {
                        'title': anime.get('title', 'Unknown'),
                        'rating': anime.get('score', 0.0) or 0.0,
                        'type': anime.get('type', 'Unknown'),
                        'episodes': f"{anime.get('episodes', '?')} eps" if anime.get('episodes') else 'Unknown',
                        'url': anime.get('url', ''),
                        'genres': genres,
                        'mal_id': anime.get('mal_id')
                    }
                    
                    self.anime_data.append(anime_info)
                    print(f"Fetched: {anime_info['title']} (Rating: {anime_info['rating']})")
                
                page += 1
                time.sleep(1)  # Longer delay for API rate limiting (was 0.5)
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                # If rate limited, wait longer and retry
                if "429" in str(e) or "Too Many Requests" in str(e):
                    print(f"Rate limited. Waiting 5 seconds before continuing...")
                    time.sleep(5)
                    continue
                break
        
        print(f"Successfully fetched {len(self.anime_data)} anime in seconds!")
        return self.anime_data
    
    def enrich_with_genres(self, limit=50):
        """Genres are already included from Jikan API - no additional work needed!"""
        print("✅ All anime already have genre data from Jikan API!")
    
    def save_to_json(self, filename='anime_data.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.anime_data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    
    def load_from_json(self, filename='anime_data.json'):
        """Load data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.anime_data = json.load(f)
            print(f"Loaded {len(self.anime_data)} anime from {filename}")
            return self.anime_data
        except FileNotFoundError:
            print(f"File {filename} not found")
            return []

def main():
    """Main function to fetch anime data"""
    scraper = MALScraper()
    
    # Always fetch fresh data (no existing data check)
    print("🚀 Fetching fresh anime data from Jikan API...")
    scraper.scrape_top_anime()  # No limit - fetch ALL anime
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
