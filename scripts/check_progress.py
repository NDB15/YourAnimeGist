#!/usr/bin/env python3
"""Quick status checker for SeriesGraph scraper"""

import json
import os
import subprocess
from datetime import datetime

def check_process():
    """Check if scraper is running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return 'scrape_seriesgraph.py' in result.stdout
    except:
        return False

def check_cache():
    """Check SeriesGraph cache status"""
    if not os.path.exists('seriesgraph_cache.json'):
        return None, 0
    
    try:
        with open('seriesgraph_cache.json', 'r') as f:
            cache = json.load(f)
            return cache.get('scraped_at'), len(cache.get('shows', []))
    except:
        return None, 0

def check_matches():
    """Check how many anime have SeriesGraph links"""
    if not os.path.exists('anime_data.json'):
        return 0, 0
    
    try:
        with open('anime_data.json', 'r') as f:
            anime_data = json.load(f)
            total = len(anime_data)
            matched = sum(1 for anime in anime_data if anime.get('seriesgraph_url'))
            return matched, total
    except:
        return 0, 0

def main():
    print("=" * 60)
    print("SeriesGraph Scraper Status")
    print("=" * 60)
    print()
    
    # Check if process is running
    is_running = check_process()
    print(f"Status: {'🟢 RUNNING' if is_running else '⚪ NOT RUNNING'}")
    print()
    
    # Check cache
    scraped_at, total_shows = check_cache()
    if scraped_at:
        print(f"SeriesGraph Cache:")
        print(f"  • Scraped at: {scraped_at}")
        print(f"  • Total shows: {total_shows:,}")
    else:
        print("SeriesGraph Cache: Not created yet")
    print()
    
    # Check matches
    matched, total = check_matches()
    if total > 0:
        percentage = (matched / total) * 100
        print(f"Anime Matching:")
        print(f"  • Matched: {matched:,} / {total:,} ({percentage:.1f}%)")
        print(f"  • Not matched: {total - matched:,}")
    else:
        print("Anime Matching: Not started yet")
    print()
    
    # Check log file
    if os.path.exists('seriesgraph.log'):
        size = os.path.getsize('seriesgraph.log')
        print(f"Log file: seriesgraph.log ({size} bytes)")
        
        # Show last few lines
        try:
            with open('seriesgraph.log', 'r') as f:
                lines = f.readlines()
                if lines:
                    print("\nLast log entries:")
                    for line in lines[-5:]:
                        print(f"  {line.rstrip()}")
        except:
            pass
    
    print()
    print("=" * 60)
    
    if is_running:
        print("\nTip: Run this script again to see updated progress")
        print("     Or check logs with: tail -f seriesgraph.log")

if __name__ == '__main__':
    main()
