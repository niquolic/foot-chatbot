from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv("config.env")
import requests
from langchain_core.tools import tool

API_KEY = os.getenv("API_SPORTS_KEY")
API_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

@tool
def search_team(team_name: str) -> str:
    """Recherche une équipe de football par nom et retourne les infos principales."""
    try:
        if not API_KEY:
            return "Erreur : La clé API n'est pas configurée. Veuillez vérifier votre fichier config.env"
            
        url = f"{API_URL}/teams"
        params = {"search": team_name}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("response"):
            return f"Aucune équipe trouvée pour '{team_name}'. Veuillez vérifier l'orthographe ou essayer un autre nom."
        
        team_data = data["response"][0]
        team = team_data["team"]
        venue = team_data.get("venue", {})
        
        return f"""Équipe : {team['name']} ({team['country']})
ID : {team['id']}
Code : {team['code']}
Fondée : {team.get('founded', 'N/A')}
Stade : {venue.get('name', 'N/A')}
Capacité : {venue.get('capacity', 'N/A')}
Surface : {venue.get('surface', 'N/A')}
Logo : {team['logo']}"""
    except Exception as e:
        return f"Erreur : {str(e)}"

@tool
def league_standings(input_str: str) -> str:
    """Retourne le classement d'un championnat (format: 'league_id, season', ex: '39, 2023')."""
    try:
        # Parse l'entrée
        parts = input_str.split(',')
        if len(parts) != 2:
            return "Format invalide. Utilisez 'league_id, season' (ex: '39, 2023')"
        
        league_id = parts[0].strip()
        season = parts[1].strip()
        
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
            played = team["all"]["played"]
            won = team["all"]["win"]
            drawn = team["all"]["draw"]
            lost = team["all"]["lose"]
            goals_for = team["all"]["goals"]["for"]
            goals_against = team["all"]["goals"]["against"]
            table.append(f"{rank}. {name} - {pts} pts (J:{played} V:{won} N:{drawn} D:{lost} BP:{goals_for} BC:{goals_against})")
        return "\n".join(table)
    except Exception as e:
        return f"Erreur : {str(e)}"

@tool
def search_league(league_name: str) -> str:
    """Recherche un championnat par nom et retourne son ID et son pays."""
    try:
        url = f"{API_URL}/leagues"
        params = {"search": league_name}
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("response"):
            return f"Aucun championnat trouvé pour '{league_name}'."
        league = data["response"][0]["league"]
        country = data["response"][0]["country"]["name"]
        return f"League : {league['name']} ({country})\nID : {league['id']}"
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

if __name__ == "__main__":
    print(search_team.invoke("manchester united"))
    print(league_standings.invoke("39, 2023"))
    print(search_league.invoke("Premier League"))