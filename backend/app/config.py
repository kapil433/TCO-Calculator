"""App configuration — env-based (local/prod)."""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API
API_V1_PREFIX = "/api/v1"

# CORS — allow frontend origin when hosted locally
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

# Optional: DB later (SQLite path)
# DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'local.db'}")
