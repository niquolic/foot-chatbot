from typing import Annotated
import os
from dotenv import load_dotenv
load_dotenv("config.env")
import requests
from langchain_core.tools import tool
from utils import create_string_input_tool

API_KEY = os.getenv("API_SPORTS_KEY")
API_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

@tool
def search_team(team_name: str) -> str:
    """Recherche une équipe de football par nom et retourne les infos principales."""
    try:
        url = f"{API_URL}/teams"
        params = {"name": team_name}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("response"):
            return f"Aucune équipe trouvée pour '{team_name}'."
        team = data["response"][0]["team"]
        country = data["response"][0]["country"]["name"]
        return f"Équipe : {team['name']} ({country})\nID : {team['id']}\nFondée : {team.get('founded', 'N/A')}\nLogo : {team['logo']}"
    except Exception as e:
        return f"Erreur : {str(e)}"

@tool
def next_fixtures(team_id: str) -> str:
    """Retourne les 3 prochains matchs d'une équipe (par ID)."""
    try:
        url = f"{API_URL}/fixtures"
        params = {"team": team_id, "next": 3}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("response"):
            return f"Aucun match à venir trouvé pour l'équipe ID {team_id}."
        fixtures = []
        for f in data["response"]:
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            date = f["fixture"]["date"]
            league = f["league"]["name"]
            fixtures.append(f"{date} : {home} vs {away} ({league})")
        return "\n".join(fixtures)
    except Exception as e:
        return f"Erreur : {str(e)}"

@tool
def league_standings(league_id: str, season: str) -> str:
    """Retourne le classement d'un championnat (par ID et saison, ex: 2023)."""
    try:
        url = f"{API_URL}/standings"
        params = {"league": league_id, "season": season}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("response"):
            return f"Aucun classement trouvé pour la ligue {league_id} saison {season}."
        standings = data["response"][0]["league"]["standings"][0]
        table = []
        for team in standings[:5]:  # Top 5
            rank = team["rank"]
            name = team["team"]["name"]
            pts = team["points"]
            table.append(f"{rank}. {name} - {pts} pts")
        return "\n".join(table)
    except Exception as e:
        return f"Erreur : {str(e)}"

@tool
def last_results(team_id: str) -> str:
    """Retourne les 3 derniers résultats d'une équipe (par ID)."""
    try:
        url = f"{API_URL}/fixtures"
        params = {"team": team_id, "last": 3}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("response"):
            return f"Aucun résultat récent trouvé pour l'équipe ID {team_id}."
        results = []
        for f in data["response"]:
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            score_home = f["goals"]["home"]
            score_away = f["goals"]["away"]
            date = f["fixture"]["date"]
            league = f["league"]["name"]
            results.append(f"{date} : {home} {score_home}-{score_away} {away} ({league})")
        return "\n".join(results)
    except Exception as e:
        return f"Erreur : {str(e)}"

league_standings_string = create_string_input_tool(league_standings, "league_standings")

if __name__ == "__main__":
    print(search_team.invoke("manchester united"))
    print(next_fixtures.invoke("87"))
    print(league_standings.invoke({"league_id": "61", "season": "2023"}))