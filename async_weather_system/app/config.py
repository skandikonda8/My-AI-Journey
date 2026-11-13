
# app/config.py

import getpass
import os


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

CITIES = [
    "New York",
    "Chicago",
    "Dallas",
    "Miami",
    "Seattle",
]

# HTTP settings
REQUEST_TIMEOUT = 10.0

# Maximum simultaneous city workflows
MAX_CONCURRENT_CITIES = 3

# PostgreSQL settings
DB_NAME = os.getenv("DB_NAME", "weather_monitoring")
DB_USER = os.getenv("DB_USER", getpass.getuser())
DB_HOST = os.getenv("DB_HOST") or None
DB_PASSWORD = os.getenv("DB_PASSWORD") or None

DB_POOL_MIN = 1
DB_POOL_MAX = 5

DB_ACQUIRE_TIMEOUT = 5.0
DB_COMMAND_TIMEOUT = 15.0

# Retry settings
MAX_RETRY_ATTEMPTS = 3
RETRY_BASE_DELAY = 0.5
RETRY_MAX_DELAY = 5.0
RETRY_JITTER = 0.2
