# Kayn Stats Analyzer

A Python tool that fetches and analyzes your League of Legends ranked statistics specifically for the Kayn champion, comparing performance between Blue Kayn (Precision primary rune) and Red Kayn (Domination primary rune).

## Features

- Fetch your ranked match history from the Riot API
- Automatically identify Kayn games and categorize them by rune choice (Blue vs Red form)
- Calculate win rates and pick rates for each form
- Export statistics to a CSV file
- Configurable search parameters (number of games, match count, region)
- Verbose and quiet modes for flexible output control

## Prerequisites

- Python 3.7+
- A Riot API key (get one at [developer.riotgames.com](https://developer.riotgames.com))
- Your League of Legends summoner name and tagline

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kayn-stats-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your credentials:

```env
RIOT_API_KEY=your_api_key_here
SUMMONER_NAME=your_summoner_name
TAGLINE=your_tagline
```

**Note:** Your summoner name and tagline are case-sensitive. You can find your tagline in your League client (usually something like "NA1" or a custom tag). Make sure there are no extra spaces or quotes in your `.env` file.

## Usage

Run the script with default parameters:
```bash
python kayn_stats.py
```

### Example Commands

```bash
# Basic usage - analyzes last 500 ranked games
python kayn_stats.py

# Scan more games for comprehensive stats
python kayn_stats.py --max_matches 1000

# If you know you have ~150 Kayn games, stop early to save API calls
python kayn_stats.py --max_matches 1000 --count 150

# Run quietly without CSV export
python kayn_stats.py --quiet --no-csv
```

### Arguments

- `--max_matches`: Maximum number of ranked matches to scan (default: 500)
- `--region`: Summoner region - EUW1, NA1, KR, JP1, BR1, etc. (default: EUW1)
- `--count`: Target number of Kayn games to fetch (optional). Only use if you know your exact Kayn game count or want to check recent games only —the script will stop early once this target is reached, saving API calls. (default: None)
- `--csv`: Export results to CSV file (default: enabled)
- `--no-csv`: Disable CSV export
- `--verbose`: Show detailed progress messages (default: enabled)
- `--quiet`: Suppress progress messages

### Example Commands

```bash
# Fetch 50 Kayn games with verbose output
python kayn_stats.py --count 50 --verbose

# Run quietly without CSV export
python kayn_stats.py --quiet --no-csv

# Scan more matches for accounts with fewer Kayn games
python kayn_stats.py --count 100 --max_matches 1000
```
⚠️ Riot API Limitation: The Riot Match-V5 API only allows fetching up to 1000 ranked matches per queue. If --max_matches is set higher than 1000, it will be automatically capped.

## Supported Regions

- **Americas:** BR1, LA1, LA2, NA1
- **Europe:** EUN1, EUW1, TR1, RU
- **Asia:** JP1, KR
- **SEA:** OC1

## Output

The script displays a summary in the console:
```
KAYN RANKED STATS
----------------
Total Kayn games: 150

Blue Kayn:
 Games: 75 (50.0% pickrate)
 Winrate: 52.5%

Red Kayn:
 Games: 75 (50.0% pickrate)
 Winrate: 48.3%

Total Kayn:
 Games: 150
 Winrate: 50.4%
```

Results are also saved to `kayn_stats.csv` for further analysis.

## How It Works

1. **Get PUUID:** Uses your summoner name and tagline to retrieve your unique player ID from the Riot API
2. **Fetch Matches:** Retrieves your ranked match IDs (filtered for Solo/Duo queue - queue ID 420)
3. **Analyze Games:** Iterates through matches, identifying Kayn games and checking the primary rune:
   - **Rune 8000 (Precision)** = Red Kayn
   - **Rune 8100 (Domination) or Rune 8300 (First Strike) Other runes fallback to blue** = Blue Kayn
4. **Calculate Stats:** Computes win rates and pick rates for each form
5. **Export:** Saves results to CSV (optional)

## Rate Limiting

The script includes built-in rate limit handling to respect Riot's API limits:

- 1.3 second delay between individual match requests
- 5 second delay when rate limited (HTTP 429)
- Batch requests of 100 matches at a time

## Troubleshooting

**"Please set RIOT_API_KEY, SUMMONER_NAME, and TAGLINE in the .env file"**
- Ensure your `.env` file exists and contains all three variables
- Check that there are no extra spaces or quotes around the values

**403 Forbidden error**
- Make sure your API key is valid and not blacklisted
- Verify your summoner name and tagline are correct and case-sensitive
- Try regenerating a fresh API key from [developer.riotgames.com](https://developer.riotgames.com)
- Wait a minute after generating a new key before using it—keys sometimes take a moment to activate

**"Rate limit hit — sleeping 5s..."**
- This is normal and expected. The script will automatically retry requests after the delay.

**No Kayn games found**
- Increase `--max_matches` to scan more of your match history
- Verify you actually have Kayn games in your ranked history

**401 Unauthorized**
- Check that your API key is correct and hasn't expired
- Regenerate a new API key if needed

## Requirements

**Python 3.7+** is required to run this tool.

See `requirements.txt`:
```txt
python-dotenv==1.0.1
requests==2.32.5
tqdm==4.67.1
```

## License

MIT License - feel free to use and modify for your own purposes.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.