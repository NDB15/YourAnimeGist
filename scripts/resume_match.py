#!/usr/bin/env python3
"""Helper script to resume matching from where it left off"""

import json

with open('anime_data.json', 'r') as f:
    anime = json.load(f)

# Find first anime without English title
first_missing_english = None
for idx, a in enumerate(anime):
    if not a.get('title_english'):
        first_missing_english = idx
        break

# Count stats
total = len(anime)
has_english = sum(1 for a in anime if a.get('title_english'))
has_sg = sum(1 for a in anime if a.get('seriesgraph_url'))

print(f"Total anime: {total:,}")
print(f"With English titles: {has_english:,} ({has_english/total*100:.1f}%)")
print(f"With SeriesGraph: {has_sg:,} ({has_sg/total*100:.1f}%)")
print()

if first_missing_english is not None:
    print(f"Resume from index: {first_missing_english}")
    print(f"Command: python3 -u scripts/match_with_english_titles.py {first_missing_english} 29619")
else:
    print("All anime have English titles!")
    print("To re-match SeriesGraph only, run the full script again.")
