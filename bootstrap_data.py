"""
One-time script to populate all missing year and image data
Run this manually: python3 bootstrap_data.py

Features:
- Saves progress every 100 anime
- Can resume if interrupted
- Won't lose data on rate limit failures
- Shows progress and ETA
"""

import requests
import json
import time
from datetime import datetime

class DataBootstrap:
    def __init__(self):
        self.base_url = "https://api.jikan.moe/v4"
        self.progress_file = "bootstrap_progress.json"
        
    def load_progress(self):
        """Load progress from last run"""
        try:
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'completed_ids': [], 'last_saved': None}
    
    def save_progress(self, completed_ids):
        """Save progress"""
        with open(self.progress_file, 'w') as f:
            json.dump({
                'completed_ids': completed_ids,
                'last_saved': datetime.now().isoformat()
            }, f)
    
    def bootstrap_all_data(self):
        """Populate all missing year and image data"""
        print("🚀 Starting data bootstrap...")
        
        # Load anime data
        with open('anime_data.json', 'r', encoding='utf-8') as f:
            anime_data = json.load(f)
        
        print(f"📊 Loaded {len(anime_data)} anime")
        
        # Load progress
        progress = self.load_progress()
        completed_ids = set(progress['completed_ids'])
        
        # Find anime needing data
        needs_data = [
            anime for anime in anime_data
            if anime.get('mal_id') and anime['mal_id'] not in completed_ids
            and (not anime.get('year') or not anime.get('image_url'))
        ]
        
        print(f"📝 {len(needs_data)} anime need data (already completed: {len(completed_ids)})")
        
        if not needs_data:
            print("✅ All anime have complete data!")
            return
        
        # Process in batches
        total = len(needs_data)
        updated = 0
        failed = 0
        start_time = time.time()
        
        for i, anime in enumerate(needs_data):
            try:
                # Fetch data
                url = f"{self.base_url}/anime/{anime['mal_id']}"
                response = requests.get(url)
                response.raise_for_status()
                
                api_data = response.json()['data']
                
                # Update year
                if not anime.get('year'):
                    year = None
                    if api_data.get('aired') and api_data['aired'].get('prop') and api_data['aired']['prop'].get('from'):
                        year = api_data['aired']['prop']['from'].get('year')
                    elif api_data.get('year'):
                        year = api_data.get('year')
                    if year:
                        anime['year'] = year
                
                # Update image_url
                if not anime.get('image_url'):
                    if api_data.get('images') and api_data['images'].get('jpg'):
                        image_url = api_data['images']['jpg'].get('large_image_url') or api_data['images']['jpg'].get('image_url', '')
                        if image_url:
                            anime['image_url'] = image_url
                
                updated += 1
                completed_ids.add(anime['mal_id'])
                
                # Progress update
                if updated % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = updated / elapsed
                    remaining = total - updated
                    eta_seconds = remaining / rate if rate > 0 else 0
                    eta_minutes = eta_seconds / 60
                    
                    print(f"  [{updated}/{total}] {anime['title'][:40]:<40} | Rate: {rate:.1f}/min | ETA: {eta_minutes:.1f}min")
                
                # Save progress every 100
                if updated % 100 == 0:
                    with open('anime_data.json', 'w', encoding='utf-8') as f:
                        json.dump(anime_data, f, indent=2, ensure_ascii=False)
                    self.save_progress(list(completed_ids))
                    print(f"  💾 Saved progress: {updated}/{total} complete")
                
                # Rate limiting - be gentle with the API
                time.sleep(0.6)  # ~100 requests per minute
                
            except Exception as e:
                if "429" in str(e):
                    print(f"  ⏸️  Rate limited at {updated}/{total}, waiting 20 seconds...")
                    time.sleep(20)
                    continue
                else:
                    failed += 1
                    print(f"  ⚠️  Failed: {anime['title']}: {e}")
                    continue
        
        # Final save
        with open('anime_data.json', 'w', encoding='utf-8') as f:
            json.dump(anime_data, f, indent=2, ensure_ascii=False)
        self.save_progress(list(completed_ids))
        
        print(f"\n✅ Bootstrap complete!")
        print(f"   Updated: {updated}/{total}")
        print(f"   Failed: {failed}")
        print(f"   Time: {(time.time() - start_time) / 60:.1f} minutes")
        
        # Check completion
        still_missing = sum(1 for a in anime_data if not a.get('year') or not a.get('image_url'))
        print(f"   Still missing data: {still_missing}")

if __name__ == "__main__":
    bootstrap = DataBootstrap()
    bootstrap.bootstrap_all_data()
