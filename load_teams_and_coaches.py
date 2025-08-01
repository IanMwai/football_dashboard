import requests
from utils.db import get_db_connection
from utils.api import HEADERS
import time

LEAGUE_ID = 39
SEASONS = [2018, 2021]

#Defining a function to get teams for a given season.
def get_teams_for_season(season):
    """Fetches all teams for a given season from the API."""
    url = f"https://v3.football.api-sports.io/teams?league={LEAGUE_ID}&season={season}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching teams for season {season}: {e}")
        return None

#Defining a function to get coaches for a given team.
def get_coaches_for_team(team_id, season):
    """Fetches all coaches for a given team from the API."""
    url = f"https://v3.football.api-sports.io/coachs?team={team_id}" 
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coaches for team {team_id}: {e}")
        return None

#Defining a function to format the teams data.
def format_teams(data):
    """Formats the teams data and returns a list of dictionaries."""
    teams = []
    if not data or "response" not in data:
        return teams
    #Looping through the teams in the response.
    for item in data["response"]:
        team_info = item["team"]
        venue = item["venue"]
        teams.append({
            "team_id": team_info["id"],
            "name": team_info["name"],
            "country": team_info["country"],
            "founded": team_info["founded"],
            "stadium_name": venue["name"]
        })
    return teams

#Defining a function to format the coaches and their history.
def format_coaches_and_history(data, team_id, season):
    """Formats the coaches and their history and returns a list of dictionaries."""
    coaches = []
    history = []
    if not data or not data.get("response"):
        return coaches, history

    #Looping through the coaches in the response.
    for item in data["response"]:
        coaches.append({
            "coach_id": item.get("id"),
            "name": item.get("name"),
            "nationality": item.get("nationality"),
        })
        history.append({
            "coach_id": item.get("id"),
            "team_id": team_id,
            "season": season
        })
    return coaches, history

#Defining a function to insert the teams into the database.
def insert_teams(teams):
    """Inserts a list of teams into the database."""
    if not teams:
        return
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                #Looping through the teams.
                for team in teams:
                    cur.execute("""
                        INSERT INTO teams (team_id, name, country, founded, stadium_name)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (team_id) DO NOTHING;
                    """, (
                        team["team_id"],
                        team["name"],
                        team["country"],
                        team["founded"],
                        team["stadium_name"]
                    ))
                conn.commit()
    except Exception as e:
        print(f"Error inserting teams: {e}")

#Defining a function to insert the coaches and their history into the database.
def insert_coaches_and_history(coaches, history):
    """Inserts a list of coaches and their history into the database."""
    if not coaches and not history:
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                #Looping through the coaches.
                for coach in coaches:
                    if not coach.get("coach_id"):
                        continue
                    cur.execute("""
                        INSERT INTO coaches (coach_id, name, nationality)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (coach_id) DO NOTHING;
                    """, (
                        coach["coach_id"],
                        coach["name"],
                        coach["nationality"]
                    ))
                
                #Looping through the coach history.
                for hist in history:
                    if not all(k in hist for k in ["coach_id", "team_id", "season"]):
                        continue
                    cur.execute("""
                        INSERT INTO coach_history (coach_id, team_id, season)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (coach_id, team_id, season) DO NOTHING;
                    """, (
                        hist["coach_id"],
                        hist["team_id"],
                        hist["season"]
                    ))
                conn.commit()
    except Exception as e:
        print(f"Error inserting coach data: {e}")

#Looping through the seasons.
for season in SEASONS:
    print(f"-- Processing Season: {season} --")
    print("📡 Fetching Premier League teams...")
    teams_data = get_teams_for_season(season)
    if teams_data:
        teams = format_teams(teams_data)
        insert_teams(teams)
        print(f"Inserted/updated {len(teams)} teams.")

        #Looping through the teams.
        for team in teams:
            team_id = team["team_id"]
            print(f"  -> Fetching coaches for team {team_id}...")
            coach_data = get_coaches_for_team(team_id, season)
            if coach_data:
                coaches, history = format_coaches_and_history(coach_data, team_id, season)
                insert_coaches_and_history(coaches, history)
                print(f"Inserted/updated {len(coaches)} coaches and their history.")
            time.sleep(1.5)