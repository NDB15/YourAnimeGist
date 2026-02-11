# Resume Guide for English Title & SeriesGraph Matching

## Current Status
The script is running in the background, processing all 29,619 anime.

**Estimated time:** ~4 hours
**Saves progress:** Every 100 anime
**Process ID:** Check with `ps aux | grep match_with_english_titles`

---

## Monitor Progress

```bash
# Watch live progress
tail -f match_all.log

# Check how many completed
python3 scripts/resume_match.py

# See last 50 lines
tail -50 match_all.log
```

---

## If Process Stops

The script saves progress every 100 anime to `anime_data.json`.

### To Resume:

1. **Check where it stopped:**
   ```bash
   python3 scripts/resume_match.py
   ```

2. **Resume from that index:**
   ```bash
   python3 -u scripts/match_with_english_titles.py START_INDEX 29619 > match_resume.log 2>&1 &
   ```
   
   Example if it stopped at 5000:
   ```bash
   python3 -u scripts/match_with_english_titles.py 5000 29619 > match_resume.log 2>&1 &
   ```

---

## When Complete

1. **Verify results:**
   ```bash
   python3 scripts/check_titles.py
   ```

2. **Commit and push:**
   ```bash
   git add anime_data.json
   git commit -m "Add English titles and SeriesGraph URLs to all anime"
   git push origin main
   ```

3. **Your site will now show:**
   - ✅ English titles when language is set to English
   - ✅ SeriesGraph buttons for matched anime

---

## Files Updated

- `anime_data.json` - Main database (auto-saved every 100 anime)
- `match_all.log` - Full log of the process

## Files Safe to Delete Later

- `match_all.log`
- `match_test.log`
- `match_resume.log` (if you resume)
- `english_titles_test.log`
