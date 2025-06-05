"""
Application Configuration

Contains all configuration constants and settings for the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

# Application Info
APP_NAME = "AI Shop Assist"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Smart Shopping with AI Assistant"

# Server Configuration
UI_SERVER_HOST = "localhost"
UI_SERVER_PORT = 8080
WEBSOCKET_SERVER_HOST = "localhost"
WEBSOCKET_SERVER_PORT = 8081
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL")
print(os.getenv("ANTHROPIC_API_KEY"))
# API Configuration
API_KEYS = {
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY")
}

# Data Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
PRODUCTS_DIR = DATA_DIR / "products"
PRODUCT_CSV = PRODUCTS_DIR / "Air Conditioners.csv"

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
LOG_FILE = "app.log"

# UI Configuration
UI_THEME = {
    "primary": "blue",
    "secondary": "gray",
    "accent": "indigo"
}

# WebSocket Configuration
WEBSOCKET_PING_INTERVAL = 20
WEBSOCKET_PING_TIMEOUT = 10
WEBSOCKET_CLOSE_TIMEOUT = 10

# Product Configuration
PRODUCTS_PER_PAGE = 20
DEFAULT_SORT_BY = "ratings"
DEFAULT_SORT_ASCENDING = False 