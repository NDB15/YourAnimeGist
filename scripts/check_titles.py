#!/usr/bin/env python3
"""Check for missing English titles in anime_data.json"""

import json

with open('anime_data.json', 'r') as f:
    anime = json.load(f)

# Find Frieren
frieren = [a for a in anime if 'frieren' in a.get('title', '').lower() or 'frieren' in a.get('title_english', '').lower()]
print("=== Frieren entries ===")
for f in frieren[:3]:
    print(f"Title: {f.get('title')}")
    print(f"English: {f.get('title_english', 'MISSING')}")
    print(f"SeriesGraph: {f.get('seriesgraph_url', 'MISSING')}")
    print()

# Count missing English titles
missing = sum(1 for a in anime if not a.get('title_english') or a.get('title_english') == a.get('title'))
print(f"\nTotal anime: {len(anime)}")
print(f"Missing/Same English titles: {missing} ({missing/len(anime)*100:.1f}%)")
