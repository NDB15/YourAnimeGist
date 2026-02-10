# YourAnimeGist

A modern anime discovery platform powered by MyAnimeList data with intelligent search and filtering.

🌐 **Live Site:** [https://youranime.me](https://youranime.me)

## Quick Links

📚 [Full Documentation](docs/README.md)  
🚀 [Deployment Guide](docs/DEPLOYMENT.md)  
📊 [SeriesGraph Integration](docs/SERIESGRAPH_README.md)

## Features

- 🎌 **Dual Language Support**: Search in English or Romaji
- 🔍 **Smart Search**: Find anime by title in both languages
- 📊 **SeriesGraph Integration**: View episode ratings and graphs
- 🎯 **Random Discovery**: Discover new anime with one click
- 📱 **Responsive Design**: Works on all devices

## Quick Start

```bash
# Serve locally
python3 -m http.server 8000

# Visit http://localhost:8000
```

## Project Structure

```
YourAnimeGist/
├── index.html              # Main application
├── anime_data.json         # Complete anime database
├── assets/                 # Images, fonts, and static files
├── scripts/                # Python utilities and scrapers
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

## Scripts

- `scripts/scraper.py` - Scrape anime from MyAnimeList via Jikan API
- `scripts/scrape_seriesgraph.py` - Build SeriesGraph database and match anime
- `scripts/check_progress.py` - Monitor scraping progress
- `scripts/validate_data.py` - Validate anime data integrity

## Contributing

See [docs/README.md](docs/README.md) for detailed information about the project.

## License

MIT License - See LICENSE file for details
