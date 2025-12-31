from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")
SUMMONER_NAME = os.getenv("SUMMONER_NAME")
TAGLINE = os.getenv("TAGLINE")

if not API_KEY or not SUMMONER_NAME or not TAGLINE:
    raise ValueError("Please set RIOT_API_KEY, SUMMONER_NAME, and TAGLINE in the .env file.")

def get_puuid(match_region):
    url = f"https://{match_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{SUMMONER_NAME}/{TAGLINE}"
    headers = {"X-Riot-Token": API_KEY}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()["puuid"]

def get_ranked_match_ids(puuid, match_region, max_matches=1000):
    headers = {"X-Riot-Token": API_KEY}
    match_ids = []
    start = 0

    while start < max_matches:
        url = f"https://{match_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {
            "queue": 420,
            "start": start,
            "count": min(100, max_matches - start)  # Cap at remaining needed matches
        }

        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()

        batch = r.json()
        if not batch:
            break

        match_ids.extend(batch)
        start += 100
        time.sleep(1)

    return match_ids


def analyze_matches(match_ids, puuid, match_region, target_kayn_games=None):
    blue_games = blue_wins = 0
    red_games = red_wins = 0
    kayn_games_found = 0

    headers = {"X-Riot-Token": API_KEY}

    from tqdm import tqdm

    for match_id in tqdm(match_ids, desc="Analyzing matches"):
        url = f"https://{match_region}.api.riotgames.com/lol/match/v5/matches/{match_id}"

        while True:
            r = requests.get(url, headers=headers)
            if r.status_code == 429:
                print("Rate limit hit — sleeping 5s...")
                time.sleep(5)
                continue
            r.raise_for_status()
            match = r.json()
            break

        for p in match["info"]["participants"]:
            if p["puuid"] == puuid and p["championName"] == "Kayn":
                kayn_games_found += 1
                primary_rune = p["perks"]["styles"][0]["style"]
                win = p["win"]

                if primary_rune == 8000:
                    # Precision -> Red kayn (Rhaast)
                    red_games += 1
                    if win:
                        red_wins += 1
                elif primary_rune in (8100, 8300):
                    #Domination or Inspiration -> Blue kayn (Shadow Assassin)
                    blue_games += 1
                    if win:
                        blue_wins += 1
                else:
                    # All others fallback to blue kayn
                    blue_games += 1
                    if win:
                        blue_wins += 1

                if VERBOSE:
                    tqdm.write(f"Kayn games found: {kayn_games_found}")

                if target_kayn_games and kayn_games_found >= target_kayn_games:
                    return blue_games, blue_wins, red_games, red_wins

        time.sleep(1.3)

    if VERBOSE:
        tqdm.write(f"Finished analyzing matches. Total Kayn games found: {kayn_games_found}")

    return blue_games, blue_wins, red_games, red_wins

import argparse

parser = argparse.ArgumentParser(description="Fetch Kayn ranked stats.")
parser.add_argument("--count", type=int, default=None, help="Target number of Kayn games to fetch")
parser.add_argument("--max_matches", type=int, default=500, help="Max number of ranked matches to scan")
parser.add_argument("--region", type=str, default="EUW1", help="Summoner region (EUW1, NA1, etc.)")
parser.add_argument("--csv", action="store_true", help="Export results to CSV file (default: True)")
parser.add_argument("--no-csv", dest="csv", action="store_false", help="Do not export results to CSV")
parser.add_argument("--verbose", action="store_true", help="Show progress messages")
parser.add_argument("--quiet", dest="verbose", action="store_false", help="Suppress progress messages")
parser.set_defaults(csv=True, verbose=True)

args = parser.parse_args()

TARGET_KAYN_GAMES = args.count
MAX_MATCHES = min(args.max_matches, 1000)

if args.max_matches > 1000 and VERBOSE:
    print("Note: Riot API limits match fetches to 1000 matches max.")

REGION = args.region
EXPORT_CSV = args.csv
VERBOSE = args.verbose


# Map platform region to match-v5 routing region
REGION_TO_MATCH_REGION = {
    "BR1": "americas",
    "EUN1": "europe",
    "EUW1": "europe",
    "JP1": "asia",
    "KR": "asia",
    "LA1": "americas",
    "LA2": "americas",
    "NA1": "americas",
    "OC1": "sea",
    "TR1": "europe",
    "RU": "europe",
}



def main():
    match_region = REGION_TO_MATCH_REGION.get(REGION.upper(), "europe")
    puuid = get_puuid(match_region)
    match_ids = get_ranked_match_ids(puuid, match_region, max_matches=MAX_MATCHES)

    blue_g, blue_w, red_g, red_w = analyze_matches(
        match_ids, 
        puuid,
        match_region,
        target_kayn_games=TARGET_KAYN_GAMES
    )

    total = blue_g + red_g

    print("\nKAYN RANKED STATS\n----------------")
    print(f"Total Kayn games: {total}")

    if blue_g:
        print(f"\nBlue Kayn:")
        print(f" Games: {blue_g} ({blue_g/total:.1%} pickrate)")
        print(f" Winrate: {blue_w/blue_g:.1%}")

    if red_g:
        print(f"\nRed Kayn:")
        print(f" Games: {red_g} ({red_g/total:.1%} pickrate)")
        print(f" Winrate: {red_w/red_g:.1%}")
    
    total_kayn_games = blue_g + red_g
    total_kayn_wins = blue_w + red_w

    if total_kayn_games > 0:
        print(f"\nTotal Kayn:")
        print(f" Games: {total_kayn_games}")
        print(f" Winrate: {total_kayn_wins/total_kayn_games:.1%}")

    # CSV export
    if EXPORT_CSV:
        import csv
        with open("kayn_stats.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Form", "Games", "Pickrate", "Winrate"])
            if blue_g:
                writer.writerow(["Blue", blue_g, f"{blue_g/total_kayn_games:.1%}", f"{blue_w/blue_g:.1%}"])
            if red_g:
                writer.writerow(["Red", red_g, f"{red_g/total_kayn_games:.1%}", f"{red_w/red_g:.1%}"])
            writer.writerow(["Total", total_kayn_games, "100%", f"{total_kayn_wins/total_kayn_games:.1%}"])
        if VERBOSE:
            print("\nKayn stats exported to kayn_stats.csv")


if __name__ == "__main__":
    main()
