"""
Configuration for the Flask backend
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"


class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-please-change-in-production")
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

    API_PREFIX = "/api"
    API_VERSION = "v1"

    PRICE_DATA_PATH = DATA_DIR / "raw" / "BrentOilPrices.csv"
    EVENTS_DATA_PATH = DATA_DIR / "events" / "enhanced_events.csv"
    CHANGEPOINT_RESULTS_PATH = MODELS_DIR / "oil_cp_results.json"

    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300


config = Config()
