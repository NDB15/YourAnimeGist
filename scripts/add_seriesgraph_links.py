"""
Add SeriesGraph links to existing anime data
Efficiently searches SeriesGraph only for anime in our database
"""

import requests
import json
import time
from urllib.parse import quote
from bs4 import BeautifulSoup

def search_seriesgraph(anime_title, anime_title_english=None):
    """
    Search SeriesGraph for an anime title
    Returns SeriesGraph URL if found, None otherwise
    """
    titles_to_try = [anime_title]
    if anime_title_english and anime_title_english != anime_title:
        titles_to_try.append(anime_title_english)
    
    for title in titles_to_try:
        try:
            search_url = f"https://www.seriesgraph.com/search?q={quote(title)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for anime result links
                # SeriesGraph typically has links in format /show/show-name or /shows/show-name
                results = soup.find_all('a', href=True)
                
                for link in results:
                    href = link.get('href', '')
                    if '/show/' in href or '/shows/' in href:
                        # Check if this link text matches our anime
                        link_text = link.get_text(strip=True).lower()
                        if any(t.lower() in link_text for t in titles_to_try):
                            full_url = href if href.startswith('http') else f"https://www.seriesgraph.com{href}"
                            return full_url
            
            time.sleep(1)  # Be respectful to the server
            
        except Exception as e:
            print(f"Error searching for {title}: {e}")
            time.sleep(2)
            continue
    
    return None

def add_seriesgraph_links(input_file='anime_data.json', output_file='anime_data.json', 
                          start_index=0, limit=None):
    """
    Add SeriesGraph links to anime data
    
    Args:
        input_file: JSON file with anime data
        output_file: Where to save updated data
        start_index: Start from this anime index (for resuming)
        limit: Only process this many anime (None = all)
    """
    print("Loading anime data...")
    with open(input_file, 'r', encoding='utf-8') as f:
        anime_data = json.load(f)
    
    total = len(anime_data)
    end_index = min(start_index + limit, total) if limit else total
    
    print(f"Processing anime {start_index + 1} to {end_index} of {total}...")
    
    found_count = 0
    not_found_count = 0
    
    for i in range(start_index, end_index):
        anime = anime_data[i]
        
        # Skip if already has SeriesGraph link
        if anime.get('seriesgraph_url'):
            print(f"[{i+1}/{total}] {anime['title']} - Already has SeriesGraph link")
            found_count += 1
            continue
        
        print(f"[{i+1}/{total}] Searching for: {anime['title']}")
        
        seriesgraph_url = search_seriesgraph(
            anime['title'], 
            anime.get('title_english')
        )
        
        if seriesgraph_url:
            anime['seriesgraph_url'] = seriesgraph_url
            found_count += 1
            print(f"  ✓ Found: {seriesgraph_url}")
        else:
            anime['seriesgraph_url'] = None
            not_found_count += 1
            print(f"  ✗ Not found on SeriesGraph")
        
        # Save progress every 10 anime
        if (i + 1) % 10 == 0:
            print(f"\n💾 Saving progress... ({found_count} found, {not_found_count} not found)")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(anime_data, f, indent=2, ensure_ascii=False)
    
    # Final save
    print(f"\n💾 Saving final results...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(anime_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Complete!")
    print(f"   Found: {found_count}")
    print(f"   Not found: {not_found_count}")
    print(f"   Total processed: {end_index - start_index}")

if __name__ == '__main__':
    import sys
    
    # Allow resuming from specific index
    start_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print("="*60)
    print("SeriesGraph Link Enrichment")
    print("="*60)
    print(f"Starting from index: {start_index}")
    if limit:
        print(f"Processing limit: {limit} anime")
    else:
        print("Processing: All remaining anime")
    print("="*60)
    print()
    
    add_seriesgraph_links(start_index=start_index, limit=limit)
