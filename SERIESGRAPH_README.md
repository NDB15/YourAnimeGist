# SeriesGraph Link Enrichment

This script adds SeriesGraph links to your existing anime database.

## How It Works

The script:
1. Reads your `anime_data.json` file
2. For each anime, searches SeriesGraph using both English and Japanese titles
3. If found, adds the `seriesgraph_url` field to that anime
4. Saves progress every 10 anime (so you can resume if interrupted)

## Usage

### Process all anime
```bash
python3 add_seriesgraph_links.py
```

### Process a limited batch (e.g., first 50 anime)
```bash
python3 add_seriesgraph_links.py 0 50
```

### Resume from a specific index (e.g., start from anime #100)
```bash
python3 add_seriesgraph_links.py 100
```

### Resume and process a batch (e.g., start from #100, do 50 anime)
```bash
python3 add_seriesgraph_links.py 100 50
```

## Tips

- **Processing is slow** (1-2 seconds per anime) to respect SeriesGraph's servers
- Progress is saved every 10 anime, so you can stop and resume anytime
- The script skips anime that already have SeriesGraph links
- Not all anime will be found on SeriesGraph (it's mostly tracking/stats focused)

## Expected Time

- 1000 anime: ~30-40 minutes
- 5000 anime: ~2-3 hours
- 10000+ anime: Process in batches of 1000-2000

## After Running

Once SeriesGraph links are added:
- Anime cards will show both "MyAnimeList" and "SeriesGraph" buttons
- Random anime results will show both links
- Links open in new tabs when clicked
