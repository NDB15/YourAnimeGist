"""Quick test to verify image URLs are being fetched"""
import requests
import json
import time

base_url = "https://api.jikan.moe/v4"
url = f"{base_url}/anime?page=1&limit=5&order_by=mal_id&sort=asc"

response = requests.get(url)
data = response.json()

anime_list = []
for anime in data['data']:
    genres = [genre['name'] for genre in anime.get('genres', [])]
    
    # Extract year
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
    
    anime_list.append(anime_info)
    print(f"✓ {anime_info['title']}")
    print(f"  Image: {image_url[:80]}...")
    print()

# Save to test file
with open('test_anime_data.json', 'w', encoding='utf-8') as f:
    json.dump(anime_list, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(anime_list)} anime to test_anime_data.json")
print(f"All have image_url: {all('image_url' in a and a['image_url'] for a in anime_list)}")
