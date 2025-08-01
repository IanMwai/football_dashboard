import requests
from utils.db import get_db_connection
from utils.api import HEADERS
import time

LEAGUE_ID = 39
SEASONS = [2018, 2021]

#Defining a function to fetch teams for a given season from the database.
def fetch_teams_for_season(season):
    """Fetches all teams for a given season from the database."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT team_id FROM coach_history WHERE season = %s;", (season,))
                teams = [row[0] for row in cur.fetchall()]
        return teams
    except Exception as e:
        print(f"Error fetching teams for season {season} from DB: {e}")
        return []

#Defining a function to get players for a given team and season.
def get_players_for_team(team_id, season):
    """Fetches all players for a given team and season from the API."""
    url = f"https://v3.football.api-sports.io/players?team={team_id}&season={season}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching players for team {team_id}, season {season}: {e}")
        return None

#Defining a function to format the players and their stats.
def format_players_and_stats(data, team_id, season):
    """Formats the players and their stats and returns a list of dictionaries."""
    players = []
    stats = []
    if not data or "response" not in data:
        return players, stats
    
    #Looping through the players in the response.
    for item in data["response"]:
        p_info = item["player"]
        s_info = item["statistics"][0]

        players.append({
            "player_id": p_info.get("id"),
            "name": p_info.get("name"),
            "nationality": p_info.get("nationality"),
            "birthdate": p_info.get("birth", {}).get("date")
        })

        games = s_info.get("games", {})
        goals = s_info.get("goals", {})
        stats.append({
            "player_id": p_info.get("id"),
            "team_id": team_id,
            "season": season,
            "appearances": games.get("appearences"),
            "goals": goals.get("total"),
            "assists": goals.get("assists"),
            "minutes_played": games.get("minutes")
        })
    return players, stats

#Defining a function to insert the players and their stats into the database.
def insert_players_and_stats(players, stats):
    """Inserts a list of players and their stats into the database."""
    if not players:
        return
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                #Looping through the players.
                for p in players:
                    cur.execute("""
                        INSERT INTO players (player_id, name, nationality, birthdate)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (player_id) DO NOTHING;
                    """, (
                        p["player_id"],
                        p["name"],
                        p["nationality"],
                        p["birthdate"]
                    ))
                
                #Looping through the player stats.
                for s in stats:
                    cur.execute("""
                        INSERT INTO player_stats (player_id, team_id, season, appearances, goals, assists, minutes_played)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (player_id, team_id, season) DO NOTHING;
                    """, (
                        s["player_id"],
                        s["team_id"],
                        s["season"],
                        s["appearances"],
                        s["goals"],
                        s["assists"],
                        s["minutes_played"]
                    ))
                conn.commit()
    except Exception as e:
        print(f"Error inserting players and stats: {e}")

#Looping through the seasons.
for season in SEASONS:
    print(f"-- Processing Season: {season} --")
    team_ids = fetch_teams_for_season(season)
    if not team_ids:
        print(f"No teams found for season {season}. Run the teams and coaches loader first.")
        continue

    #Looping through the teams.
    for team_id in team_ids:
        print(f"  -> Fetching players for team {team_id}...")
        players_data = get_players_for_team(team_id, season)
        if players_data:
            players, stats = format_players_and_stats(players_data, team_id, season)
            insert_players_and_stats(players, stats)
            print(f"Inserted/updated {len(players)} players and their stats.")
        time.sleep(1.5)