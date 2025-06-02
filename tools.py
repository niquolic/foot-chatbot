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
        # Vérifier la clé API
        if not API_KEY:
            return "Erreur : La clé API n'est pas configurée. Veuillez vérifier votre fichier config.env"
            
        print(f"Utilisation de la clé API : {API_KEY[:5]}...")
        
        url = f"{API_URL}/teams"
        params = {"search": team_name}
        
        print(f"URL de la requête : {url}")
        print(f"Paramètres : {params}")
        print(f"Headers : {HEADERS}")
        
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        print(f"Status Code : {response.status_code}")
        print(f"Response Headers : {dict(response.headers)}")
        print(f"Response Content : {response.text[:500]}")
        
        response.raise_for_status()
        data = response.json()
        
        if not data.get("response"):
            return f"Aucune équipe trouvée pour '{team_name}'. Veuillez vérifier l'orthographe ou essayer un autre nom."
        
        # Accès corrigé aux données de l'équipe
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
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête : {str(e)}")
        return f"Erreur de connexion à l'API : {str(e)}"
    except Exception as e:
        print(f"Erreur inattendue : {str(e)}")
        return f"Erreur inattendue : {str(e)}"

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

def parse_league_standings_input(input_str: str) -> tuple[str, str]:
    """Parse l'entrée string en league_id et season."""
    try:
        league_id, season = input_str.split(",")
        return league_id.strip(), season.strip()
    except:
        return "39", "2023"  # Valeurs par défaut pour Premier League

@tool
def league_standings_string(input_str: str) -> str:
    """Version string de la fonction league_standings."""
    league_id, season = parse_league_standings_input(input_str)
    return league_standings(league_id, season)

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

if __name__ == "__main__":
    print(search_team.invoke("manchester united"))
    print(next_fixtures.invoke("87"))
    print(league_standings.invoke({"league_id": "61", "season": "2023"}))
    print(search_league.invoke("Ligue 1"))