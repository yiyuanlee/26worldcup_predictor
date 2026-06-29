import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = Path("/tmp/wc_cache") if os.getenv("VERCEL") else DATA_DIR / "cache"
MODEL_DIR = PROJECT_ROOT / "models"
STATIC_DIR = PROJECT_ROOT / "static"
PUBLIC_DIR = PROJECT_ROOT / "public"

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "")
DEFAULT_COMPETITION = os.getenv("DEFAULT_COMPETITION", "WC")
DEFAULT_SPORT = os.getenv("DEFAULT_SPORT", "soccer_fifa_world_cup")
WC_MODEL_FILENAME = "wc_predictor.joblib"
FORM_WINDOW = int(os.getenv("FORM_WINDOW", "5"))
H2H_WINDOW = int(os.getenv("H2H_WINDOW", "10"))
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

ODDS_API_BASE = "https://api.the-odds-api.com/v4"
FOOTBALL_DATA_BASE = "https://api.football-data.org/v4"

# football-data.org 联赛代码 ↔ The Odds API sport key
COMPETITION_MAP = {
    "WC": {
        "name": "世界杯",
        "odds_sport": "soccer_fifa_world_cup",
        "teams": 32,
        "type": "international",
        "icon": "🏆",
    },
    "PL": {"name": "英超", "odds_sport": "soccer_epl", "teams": 20, "type": "club"},
    "PD": {"name": "西甲", "odds_sport": "soccer_spain_la_liga", "teams": 20, "type": "club"},
    "SA": {"name": "意甲", "odds_sport": "soccer_italy_serie_a", "teams": 20, "type": "club"},
    "BL1": {"name": "德甲", "odds_sport": "soccer_germany_bundesliga", "teams": 18, "type": "club"},
    "FL1": {"name": "法甲", "odds_sport": "soccer_france_ligue_one", "teams": 18, "type": "club"},
}

INTERNATIONAL_COMPETITIONS = {k for k, v in COMPETITION_MAP.items() if v.get("type") == "international"}

for d in (DATA_DIR, CACHE_DIR, MODEL_DIR, STATIC_DIR):
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
