#!/usr/bin/env python3
"""Check status of all background processes and resume if needed"""

import subprocess
import json
import os
from datetime import datetime

def check_process_running(pattern):
    """Check if a process matching the pattern is running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return pattern in result.stdout
    except:
        return False

def get_seriesgraph_status():
    """Check SeriesGraph scraping status"""
    is_running = check_process_running('scrape_seriesgraph.py')
    
    cache_exists = os.path.exists('seriesgraph_cache.json')
    total_shows = 0
    scraped_at = None
    
    if cache_exists:
        try:
            with open('seriesgraph_cache.json', 'r') as f:
                cache = json.load(f)
                total_shows = len(cache.get('shows', []))
                scraped_at = cache.get('scraped_at')
        except:
            pass
    
    # Check log
    log_exists = os.path.exists('seriesgraph_rescrape.log')
    last_log = None
    if log_exists:
        try:
            with open('seriesgraph_rescrape.log', 'r') as f:
                lines = f.readlines()
                if lines:
                    last_log = lines[-1].strip()
        except:
            pass
    
    return {
        'running': is_running,
        'cache_shows': total_shows,
        'scraped_at': scraped_at,
        'last_log': last_log
    }

def get_matcher_status():
    """Check English title matching status"""
    is_running = check_process_running('match_with_english_titles.py')
    
    try:
        with open('anime_data.json', 'r') as f:
            anime = json.load(f)
            total = len(anime)
            has_english = sum(1 for a in anime if a.get('title_english'))
            has_sg = sum(1 for a in anime if a.get('seriesgraph_url'))
            
            return {
                'running': is_running,
                'total': total,
                'has_english': has_english,
                'has_sg': has_sg,
                'english_pct': (has_english / total * 100) if total > 0 else 0,
                'sg_pct': (has_sg / total * 100) if total > 0 else 0
            }
    except:
        return {'running': is_running, 'total': 0, 'has_english': 0, 'has_sg': 0}

def main():
    print("="*70)
    print("YourAnimeGist Background Processes Status")
    print("="*70)
    print()
    
    # Check SeriesGraph scraper
    sg_status = get_seriesgraph_status()
    print("📊 SeriesGraph Scraper:")
    print(f"  Status: {'🟢 RUNNING' if sg_status['running'] else '⚪ STOPPED'}")
    print(f"  Shows cached: {sg_status['cache_shows']:,}")
    if sg_status['last_log']:
        print(f"  Last activity: {sg_status['last_log']}")
    print()
    
    if not sg_status['running'] and sg_status['cache_shows'] < 4000:
        print("  ⚠️  SeriesGraph scraping incomplete!")
        print("  Resume with:")
        print("    python3 -u scripts/scrape_seriesgraph.py --scrape > seriesgraph_rescrape.log 2>&1 &")
        print()
    
    # Check matcher
    matcher_status = get_matcher_status()
    print("🔤 English Title & SeriesGraph Matcher:")
    print(f"  Status: {'🟢 RUNNING' if matcher_status['running'] else '⚪ STOPPED'}")
    print(f"  Total anime: {matcher_status['total']:,}")
    print(f"  With English titles: {matcher_status['has_english']:,} ({matcher_status['english_pct']:.1f}%)")
    print(f"  With SeriesGraph: {matcher_status['has_sg']:,} ({matcher_status['sg_pct']:.1f}%)")
    print()
    
    if not matcher_status['running'] and matcher_status['english_pct'] < 100:
        print("  ⚠️  English title matching incomplete!")
        if sg_status['running'] or sg_status['cache_shows'] < 4000:
            print("  ⏳ Wait for SeriesGraph scraping to complete first")
        else:
            print("  Resume with:")
            print("    python3 scripts/resume_match.py  # Get the exact command")
        print()
    
    print("="*70)
    print()
    
    # Summary
    if sg_status['running'] or matcher_status['running']:
        print("✅ Processes are running. Check back later!")
    elif sg_status['cache_shows'] >= 4000 and matcher_status['english_pct'] >= 99:
        print("🎉 All processes complete!")
        print("   Ready to commit and push changes.")
    else:
        print("⚠️  Some processes need to be resumed (see commands above)")

if __name__ == '__main__':
    main()
