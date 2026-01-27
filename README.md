# YourAnimeGist

Discover anime from MyAnimeList based on ratings and genres. A static anime discovery website with automatic daily updates.

## Features

- Random Anime Picker - Get a random anime suggestion based on your filters
- Advanced Filtering - Filter by rating range and multiple genres
- Complete Database - Access to 10,000+ anime from MyAnimeList
- BRC-Inspired Design - Bomb Rush Cyberfunk aesthetic with video backgrounds and sound effects
- Fully Autonomous - Automatic daily updates via GitHub Actions
- Zero Downtime - Static site means no server downtime during updates
- Responsive Design - Works on desktop and mobile devices

## Live Demo

Visit the live site: [Your GitHub Pages URL will go here]

## Architecture

This project uses a fully static architecture optimized for GitHub Pages:

- Frontend: Pure HTML/CSS/JavaScript (no server needed)
- Data: Client-side JSON loading for instant filtering
- Updates: GitHub Actions runs scraper daily at 3 AM UTC
- Hosting: GitHub Pages (free, fast, reliable)

### How It Works

1. GitHub Actions runs `scraper.py` daily at 3 AM UTC
2. Scraper fetches all anime from Jikan API (MyAnimeList's unofficial API)
3. Updated `anime_data.json` is committed to the repository
4. GitHub Pages automatically deploys the updated site
5. Users see fresh data after refreshing (no downtime)

## Deployment Instructions

### Step 1: Fork or Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/YourAnimeGist.git
cd YourAnimeGist
```

### Step 2: Enable GitHub Actions

1. Go to your repository Settings > Actions > General
2. Under "Workflow permissions", select Read and write permissions
3. Click Save

### Step 3: Enable GitHub Pages

1. Go to Settings > Pages
2. Under "Source", select Deploy from a branch
3. Select main branch and / (root) folder
4. Click Save

### Step 4: Run Initial Data Fetch

Option A: Trigger GitHub Action (Recommended)
1. Go to Actions tab
2. Select Update Anime Database workflow
3. Click Run workflow > Run workflow
4. Wait 2-4 hours for complete data fetch

Option B: Run Locally Then Push
```bash
pip install requests
python scraper.py
git add anime_data.json
git commit -m "Initial anime database"
git push
```

### Step 5: Access Your Site

Your site will be live at: `https://YOUR_USERNAME.github.io/YourAnimeGist/`

## Local Development

### Prerequisites

- Python 3.9+
- requests library

### Run Scraper Locally

```bash
# Install dependencies
pip install requests

# Fetch anime data (takes 2-4 hours for complete database)
python scraper.py

# Open index.html in your browser
open index.html
```

### Test Static Site Locally

```bash
# Use Python's built-in HTTP server
python3 -m http.server 8000

# Visit http://localhost:8000 in your browser
```

## Project Structure

```
YourAnimeGist/
├── index.html              # Main website (static HTML)
├── anime_data.json         # Anime database (auto-updated daily)
├── scraper.py             # Data fetcher for Jikan API
├── static/
│   ├── img/
│   │   └── BRBackground.webm  # Video background
│   └── sounds/            # Sound effects (combo sounds, DJ scratch)
├── .github/
│   └── workflows/
│       └── update-anime-data.yml  # GitHub Actions workflow
└── README.md              # This file
```

## Automatic Updates

The site automatically updates daily at 3:00 AM UTC via GitHub Actions. The workflow:

1. Runs `scraper.py` to fetch latest anime data
2. Checks if data has changed
3. Commits updated `anime_data.json` if changes detected
4. GitHub Pages auto-deploys the update

Manual Trigger: Go to Actions > Update Anime Database > Run workflow

## Customization

### Change Update Schedule

Edit .github/workflows/update-anime-data.yml:

```yaml
schedule:
  - cron: '0 3 * * *'  # Change time (UTC format)
```

### Modify Styling

Edit colors, fonts, and layout in the `<style>` section of index.html.

### Add More Data Fields

Modify `scraper.py` to include additional anime metadata from Jikan API.

## Data Source

Data is fetched from Jikan API v4 (unofficial MyAnimeList API):
- Endpoint: `https://api.jikan.moe/v4/anime`
- Rate Limit: approximately 3 requests/second
- Complete database fetch: 2-4 hours (10,000+ anime)

## Important Notes

### Rate Limiting
- Jikan API has rate limits (approximately 3 requests/second)
- Scraper includes automatic backoff (1s delay, 5s on rate limit)
- Full fetch takes 2-4 hours

### GitHub Actions Minutes
- Free tier: 2,000 minutes/month
- Daily updates use approximately 30-120 minutes each
- Estimate: approximately 900-3,600 minutes/month (within free tier)

### Data Freshness
- Updates daily at 3 AM UTC
- Users must refresh page to see updates
- No automatic real-time updates (static site)

## Troubleshooting

### Site not loading data
- Check if `anime_data.json` exists in repository
- Run the scraper manually or trigger GitHub Action
- Wait for it to complete (check Actions tab for progress)

### GitHub Actions failing
- Ensure workflow permissions are set to "Read and write"
- Check Actions logs for specific error messages
- May be Jikan API downtime (try again later)

### Slow initial load
- Large `anime_data.json` (1-5MB) takes time to download
- Consider compressing JSON or implementing pagination
- Trade-off: Client-side filtering is instant after load

## License

This project uses data from MyAnimeList via the Jikan API. Please respect their terms of service and rate limits.

## Credits

- MyAnimeList - Anime data source
- Jikan API - Unofficial MAL REST API
- Bomb Rush Cyberfunk - Visual inspiration and audio assets

## Links

- [Live Site](#)
- [Jikan API Documentation](https://docs.api.jikan.moe/)
- [MyAnimeList](https://myanimelist.net/)
