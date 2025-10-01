"""
MR Bot Configuration
Handles bot settings, API keys, and MR-specific configurations
"""
import os
import sys

# Add parent directory to access shared utilities
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment from mr_bot directory
from dotenv import load_dotenv
# Try multiple possible .env file locations
env_paths = [
    os.path.join(os.path.dirname(__file__), '.env'),  # Same directory as config.py
    os.path.join(os.path.dirname(__file__), '..', '.env'),  # Parent directory
    '.env'  # Current working directory
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('MR_BOT_TOKEN', '')

# Google Sheets Configuration  
GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'pharmagiftapp-60fb5a6a3ca9.json')
MR_SPREADSHEET_ID = os.getenv('MR_SPREADSHEET_ID', '')

# MR Bot Specific Settings
LOCATION_SESSION_DURATION = int(os.getenv('LOCATION_SESSION_DURATION', '900'))  # 15 minutes (900 seconds)
LOCATION_WARNING_THRESHOLD = 300  # Warn 5 minutes before expiry  
MAX_ENTRIES_PER_SESSION = 20  # Maximum entries per location session

# Sheet Names
DAILY_VISITS_SHEET = "Daily_Visits"
EXPENSES_SHEET = "Expenses" 
LOCATION_LOG_SHEET = "Location_Log"

# MR Authentication - Parse from environment
authorized_ids_str = os.getenv('AUTHORIZED_MR_IDS', '1201911108')
AUTHORIZED_MR_IDS = [int(id.strip()) for id in authorized_ids_str.split(',') if id.strip()]

# Admin ID
ADMIN_ID = int(os.getenv('ADMIN_ID', '1201911108'))

# Gemini API Keys (for advanced parsing)
GEMINI_API_KEYS = [
    os.getenv('GEMINI_API_KEY', ''),
    os.getenv('GEMINI_API_KEY_2', ''),
    os.getenv('GEMINI_API_KEY_3', '')
]

# Location Settings
GPS_REQUIRED = True
ALLOW_MANUAL_LOCATION = True  # Fallback if GPS fails
MIN_LOCATION_ACCURACY = 100  # meters

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "mr_bot.log"
