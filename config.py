"""
Configuration module for Telegram Signal Bot
Loads credentials from .env and defines bot settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram API Credentials (from my.telegram.org)
API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
PHONE_NUMBER = os.getenv('PHONE_NUMBER', '')

# Group/Channel IDs
# Replace these with actual IDs from your groups
# Use @userinfobot or check logs to find group IDs
SOURCE_GROUP_ID = -1002095814822  # Group to monitor for signals
TARGET_GROUP_ID = -758265670  # Group to forward signals to

# Bot Settings
FORWARD_DELAY = 2  # Seconds to wait between forwards (anti-spam protection)
SESSION_NAME = 'sessions/user'  # Session file location

# Logging Configuration
LOG_FILE = 'logs/bot.log'
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# Validate required credentials
if not API_ID or not API_HASH or not PHONE_NUMBER:
    raise ValueError(
        "Missing required credentials! Please create a .env file with:\n"
        "- API_ID\n"
        "- API_HASH\n"
        "- PHONE_NUMBER\n"
        "See .env.example for template."
    )
