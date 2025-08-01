import requests
from utils.db import get_db_connection
from utils.api import HEADERS
import time

LEAGUE_ID = 39
SEASONS = [2018, 2021]

#Defining a function to fetch known player and team IDs from the database.
def fetch_known_ids():
    """Fetches all known player and team IDs from the database."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT player_id FROM players;")
                player_ids = {row[0] for row in cur.fetchall()}
                cur.execute("SELECT team_id FROM teams;")
                team_ids = {row[0] for row in cur.fetchall()}
        return player_ids, team_ids
    except Exception as e:
        print(f"Error fetching known IDs from DB: {e}")
        return set(), set()

#Defining a function to get transfers for a given team.
def get_transfers_for_team(team_id):
    """Fetches all transfers for a given team from the API."""
    url = f"https://v3.football.api-sports.io/transfers?team={team_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching transfers for team {team_id}: {e}")
        return None

#Defining a function to format the transfers data.
def format_transfers(data, season, known_player_ids, known_team_ids):
    """Formats the transfers data and returns a list of dictionaries."""
    transfers = []
    if not data or "response" not in data:
        return transfers
    
    #Looping through the transfers in the response.
    for item in data["response"]:
        player_id = item["player"]["id"]
        if player_id not in known_player_ids:
            continue

        #Looping through the transfers for the player.
        for t in item.get("transfers", []):
            transfer_date = t.get("date")
            if not transfer_date or not transfer_date.startswith(str(season)):
                continue

            teams = t.get("teams", {})
            from_team = teams.get("out", {})
            to_team = teams.get("in", {})

            from_team_id = from_team.get("id")
            to_team_id = to_team.get("id")

            if from_team_id and from_team_id not in known_team_ids:
                continue
            if to_team_id and to_team_id not in known_team_ids:
                continue
            
            fee_str = t.get("type")
            fee = None
            if fee_str and "€" in fee_str:
                try:
                    fee_val = fee_str.split("€")[1].strip()
                    if 'M' in fee_val:
                        fee = float(fee_val.replace('M', '')) * 1000000
                    elif 'K' in fee_val:
                        fee = float(fee_val.replace('K', '')) * 1000
                    else:
                        fee = float(fee_val)
                except (ValueError, IndexError):
                    fee = None

            transfers.append({
                "player_id": player_id,
                "from_team_id": from_team_id,
                "to_team_id": to_team_id,
                "transfer_fee": fee,
                "season": season,
                "date": transfer_date
            })
    return transfers

#Defining a function to insert the transfers into the database.
def insert_transfers(transfers):
    """Inserts a list of transfers into the database."""
    if not transfers:
        return
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                #Looping through the transfers.
                for t in transfers:
                    cur.execute("""
                        INSERT INTO transfers (player_id, from_team_id, to_team_id, transfer_fee, season, date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (player_id, from_team_id, to_team_id, date) DO NOTHING;
                    """, (
                        t["player_id"],
                        t["from_team_id"],
                        t["to_team_id"],
                        t["transfer_fee"],
                        t["season"],
                        t["date"]
                    ))
                conn.commit()
    except Exception as e:
        print(f"Error inserting transfers: {e}")

#Getting the known player and team IDs from the database.
known_player_ids, known_team_ids = fetch_known_ids()
if not known_team_ids:
    print("No teams found in the database. Run the teams and coaches loader first.")
    exit()

#Looping through the seasons.
for season in SEASONS:
    print(f"-- Processing Season: {season} --")
    #Looping through the known teams.
    for team_id in known_team_ids:
        print(f"  -> Fetching transfers for team {team_id}...")
        transfers_data = get_transfers_for_team(team_id)
        if transfers_data:
            transfers = format_transfers(transfers_data, season, known_player_ids, known_team_ids)
            insert_transfers(transfers)
            print(f"Inserted/updated {len(transfers)} transfers.")
        time.sleep(1.5)