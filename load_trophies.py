import requests
from utils.db import get_db_connection
from utils.api import HEADERS
import time

#Defining a function to fetch known player and coach IDs from the database.
def fetch_players_and_coaches():
    """Fetches all known player and coach IDs from the database."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT player_id FROM players;")
                players = [row[0] for row in cur.fetchall()]
                cur.execute("SELECT coach_id FROM coaches;")
                coaches = [row[0] for row in cur.fetchall()]
        return players, coaches
    except Exception as e:
        print(f"Error fetching players and coaches from DB: {e}")
        return [], []

#Defining a function to get trophies for a given entity (player or coach).
def get_trophies(entity_id, entity_type):
    """Fetches all trophies for a given entity (player or coach) from the API."""
    url = f"https://v3.football.api-sports.io/trophies?{entity_type}={entity_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trophies for {entity_type} {entity_id}: {e}")
        return None

#Defining a function to format the trophies data.
def format_trophies(data, entity_id, entity_type):
    """Formats the trophies data and returns a list of dictionaries."""
    trophies = []
    if not data or not data.get("response"):
        return trophies

    #Looping through the trophies in the response.
    for t in data["response"]:
        place = t.get("place")
        if place in ["Winner", "Runner-up"]:
            season_str = t.get("season")
            season = None
            if season_str and isinstance(season_str, str) and season_str.isdigit():
                season = int(season_str)
            elif isinstance(season_str, int):
                season = season_str

            trophy = {
                "name": t.get("league"),
                "season": season,
                "result": "Winner" if place == "Winner" else "Finalist"
            }
            if entity_type == 'player':
                trophy['player_id'] = entity_id
                trophy['coach_id'] = None
            else:
                trophy['player_id'] = None
                trophy['coach_id'] = entity_id
            trophies.append(trophy)

    return trophies

#Defining a function to insert the trophies into the database.
def insert_trophies(trophies):
    """Inserts a list of trophies into the database."""
    if not trophies:
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                #Looping through the trophies.
                for trophy in trophies:
                    if not all(k in trophy for k in ["name", "season"]):
                        continue
                    cur.execute("""
                        INSERT INTO trophies (player_id, coach_id, name, season, result)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (player_id, coach_id, name, season) DO NOTHING;
                    """, (
                        trophy["player_id"],
                        trophy["coach_id"],
                        trophy["name"],
                        trophy["season"],
                        trophy["result"]
                    ))
                conn.commit()
    except Exception as e:
        print(f"Error inserting trophies: {e}")

#Printing a message to indicate that the players and coaches are being fetched.
print("📦 Fetching players and coaches from DB...")
#Getting the known player and coach IDs from the database.
player_ids, coach_ids = fetch_players_and_coaches()

#Looping through the players.
if player_ids:
    for player_id in player_ids:
        print(f"📡 Fetching trophies for player {player_id}...")
        data = get_trophies(player_id, 'player')
        if data:
            trophies = format_trophies(data, player_id, 'player')
            if trophies:
                insert_trophies(trophies)
                print(f"Inserted/updated {len(trophies)} trophies.")
        time.sleep(1.5)

#Looping through the coaches.
if coach_ids:
    for coach_id in coach_ids:
        print(f"📡 Fetching trophies for coach {coach_id}...")
        data = get_trophies(coach_id, 'coach')
        if data:
            trophies = format_trophies(data, coach_id, 'coach')
            if trophies:
                insert_trophies(trophies)
                print(f"Inserted/updated {len(trophies)} trophies.")
        time.sleep(1.5)