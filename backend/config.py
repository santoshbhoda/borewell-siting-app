"""
Backend Configuration for BSMA GeoAI Borewell Siting Service
Supports Cloud Deployment (Supabase / Neon / Render / Local).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Application Settings
APP_NAME = "BSMA GeoAI Borewell Siting Platform API"
API_V1_PREFIX = "/api/v1"
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# Database Connection (Supabase / Neon / Render / SQLite fallback for local test)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./borewell_local.db" # Default fallback for local testing without active cloud DB
)

# CORS Allowed Origins
CORS_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "https://*.pages.dev",
    "https://*.onrender.com",
    "*"
]

# Hydrogeological Pilot Settings
PILOT_STATE = "Telangana"
PILOT_BASIN = "Musi Sub-Basin (Yadadri-Bhuvanagiri / Jangaon Belt)"
