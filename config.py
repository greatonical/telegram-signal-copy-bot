"""
Configuration module for Telegram Signal Bot
Loads credentials from .env and defines bot settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram API Credentials (from my.telegram.org)
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")

# Group/Channel IDs (Legacy - kept for backward compatibility)
# Replace these with actual IDs from your groups
# Use @userinfobot or check logs to find group IDs
SOURCE_GROUP_ID = -1003354980634  # Group to monitor for signals
TARGET_GROUP_ID = -1003657608293  # Group to forward signals to

# ============================================================================
# FORWARD MAPPINGS - Flexible Source to Target Configuration
# ============================================================================
# Each mapping is a dictionary with:
#   - source_id: Group/Channel ID to monitor (required)
#   - target_id: Group/Channel ID to forward to (required)
#   - source_topic_id: Specific topic ID in source (optional, for forum groups)
#   - target_topic_id: Specific topic ID in target (optional, for forum groups)
#
# Examples:
# 1. Forward entire group to another group:
#    {"source_id": -1001234567890, "target_id": -1009876543210}
#
# 2. Forward specific topic to another topic:
#    {"source_id": -1001234567890, "source_topic_id": 5,
#     "target_id": -1009876543210, "target_topic_id": 242}
#
# 3. Forward channel to group topic:
#    {"source_id": -1001234567890, "target_id": -1009876543210, "target_topic_id": 1}
#
# 4. Forward entire group to a specific topic (group → topic):
#    {"source_id": -1001234567890, "target_id": -1009876543210, "target_topic_id": 5}
#
# 5. Forward specific topic to entire group (topic → group):
#    {"source_id": -1001234567890, "source_topic_id": 5, "target_id": -1009876543210}

FORWARD_MAPPINGS = [
    # ========================================================================
    # TOPIC TO TOPIC MAPPINGS (Forum Groups)
    # ========================================================================
    # Topic to Topic: Synergy topic to Synergy topic
    {
        "source_id": -1003354980634,
        "source_topic_id": 394,  # Synergy
        "target_id": -1003657608293,
        "target_topic_id": 258,  # Synergy
    },
    # Topic to Topic: PulseX topic to Pulse X topic
    {
        "source_id": -1003354980634,
        "source_topic_id": 4,  # PulseX
        "target_id": -1003657608293,
        "target_topic_id": 255,  # Pulse X
    },
    # Topic to Topic: Nova topic to Nova topic
    {
        "source_id": -1003354980634,
        "source_topic_id": 5,  # Nova
        "target_id": -1003657608293,
        "target_topic_id": 276,  # Nova
    },
    # Topic to Topic: Announcements to General
    {
        "source_id": -1003354980634,
        "source_topic_id": 1,  # Announcements
        "target_id": -1003657608293,
        "target_topic_id": 1,  # General
    },
    {
        "source_id": -1003719256941,  # Pro Trader Results channel
        "target_id": -1003865081218,  # Pro Traders group
    },
    {
        "source_id": -1003157087401,  # IQ Ideas channel
        "target_id": -1003657608293,  # Pro Traders group
        "target_topic_id": 268,  # IQ ideas topic
    },
    {
        "source_id": -1003683230844,  # Infinity Pips channel
        "target_id": -1003657608293,  # Pro Traders group
        "target_topic_id": 259,  # Infinity x Synergy Pips topic
    },
    {
        "source_id": -1002871747055,  # OBIOFLAGOS FX COMMUNITY
        "target_id": -1003621804175,  # OBI THE GOD FX community (Africa)
    },
    {
        "source_id": -1003771929527,  # Gilly Options Signals
        "target_id": -1003850746623,  # Binary Option signals
    },
    {
        # Scheduled: Gilly Options → Free Signals (Mon/Wed/Fri 17:00–20:00)
        # Schedule is enforced in bot.py via SCHEDULED_FORWARDING config.
        "source_id": -1003771929527,  # Gilly Options Signals
        "target_id": -1002885383779,  # Free Signals channel
    },
    # ========================================================================
    # CHANNEL TO GROUP/TOPIC MAPPINGS
    # ========================================================================
    # Example: Copy from a channel to a specific topic in target group
    # Uncomment and replace with your channel ID:
    # {
    #     "source_id": -1003719256941,  # Pro Trader Results channel
    #     "target_id": -1003657608293,  # Pro Traders group
    #     "target_topic_id": 268,  # IQ ideas topic
    # },
    # Example: Copy from a channel to entire group (no specific topic)
    # {
    #     "source_id": -1003157087401,  # IQ Ideas channel
    #     "target_id": -1003657608293,  # Pro Traders group
    # },
    # ========================================================================
    # GROUP TO GROUP MAPPINGS
    # ========================================================================
    # Example: Copy entire source group to entire target group
    # {
    #     "source_id": -1003354980634,  # Pro Trader group
    #     "target_id": -1003428541419,  # RESULT GROUP
    # },
    # ========================================================================
    # GROUP TO CHANNEL MAPPINGS
    # ========================================================================
    # Example: Copy from a group to a channel
    # {
    #     "source_id": -1003354980634,  # Pro Trader group
    #     "target_id": -1003719256941,  # Pro Trader Results channel
    # },
    # ========================================================================
    # MIXED EXAMPLES: Group ↔ Topic forwarding
    # ========================================================================
    # Example: Forward entire source group to a specific target topic
    # (All messages from any topic in source → one specific topic in target)
    # {
    #     "source_id": -1003354980634,  # Entire source group
    #     "target_id": -1003657608293,
    #     "target_topic_id": 268,  # IQ ideas topic
    # },
    # Example: Forward specific source topic to entire target group
    # (Messages from one topic → main group chat, not recommended for forum groups)
    # {
    #     "source_id": -1003354980634,
    #     "source_topic_id": 394,  # Synergy topic only
    #     "target_id": -1003657608293,  # Entire target group (no specific topic)
    # },
]

# Bot Settings
FORWARD_DELAY = 2  # Seconds to wait between forwards (anti-spam protection)
SESSION_NAME = "sessions/user"  # Session file location

# Logging Configuration
LOG_FILE = "logs/bot.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# ============================================================================
# FEATURE FLAGS
# ============================================================================
# Set to "false" in .env to disable without removing any other config.
# Default: both enabled.
ENABLE_FORWARDING = os.getenv("ENABLE_FORWARDING", "true").lower() == "true"
ENABLE_AUTO_TRADING = os.getenv("ENABLE_AUTO_TRADING", "true").lower() == "true"

# ============================================================================
# AUTO-TRADING CONFIGURATION
# ============================================================================
IQ_OPTION_EMAIL = os.getenv("IQ_OPTION_EMAIL", "")
IQ_OPTION_PASSWORD = os.getenv("IQ_OPTION_PASSWORD", "")
TRADE_AMOUNT = float(os.getenv("TRADE_AMOUNT", "1.0"))
MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "10.0"))
USE_PRACTICE_ACCOUNT = os.getenv("USE_PRACTICE_ACCOUNT", "true").lower() == "true"

# Maximum seconds to wait for an upcoming signal minute.
# Signals arriving more than this many seconds before their scheduled minute are skipped.
# Default 120 = wait at most 2 minutes.
SIGNAL_MAX_WAIT_SECONDS = int(os.getenv("SIGNAL_MAX_WAIT_SECONDS", "120"))

# Parse comma-separated list of group IDs
AUTO_TRADE_SOURCES_STR = os.getenv("AUTO_TRADE_SOURCES", "")
AUTO_TRADE_SOURCES = set()
if AUTO_TRADE_SOURCES_STR:
    try:
        AUTO_TRADE_SOURCES = {
            int(x.strip()) for x in AUTO_TRADE_SOURCES_STR.split(",") if x.strip()
        }
    except ValueError:
        pass

# ============================================================================
# SCHEDULED FORWARDING CONFIGURATION
# ============================================================================
# Some source→target pairs should only forward messages during certain days
# and time windows. Configure each rule here.
#
# Fields:
#   source_id   : Source channel/group ID to apply the schedule to
#   target_id   : Target channel/group ID (must match a FORWARD_MAPPINGS entry)
#   days        : List of weekday numbers when forwarding is allowed
#                 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday,
#                 4 = Friday, 5 = Saturday, 6 = Sunday
#   all_day     : If True, forward at any time on the allowed days (ignores
#                 start_time / end_time)
#   start_time  : "HH:MM" – start of the forwarding window (24-hour clock)
#   end_time    : "HH:MM" – end of the forwarding window (24-hour clock)
#
# To allow forwarding on Mon / Wed / Fri between 17:00 and 20:00:
#   days=[0, 2, 4], all_day=False, start_time="17:00", end_time="20:00"
#
# To allow forwarding all day on Mon / Wed / Fri:
#   days=[0, 2, 4], all_day=True
#
# Leave SCHEDULED_FORWARDING as an empty list [] to disable scheduling
# (all FORWARD_MAPPINGS entries forward without time restrictions).

SCHEDULED_FORWARDING = [
    {
        "source_id": -1003771929527,  # Gilly Options Signals
        "target_id": -1002885383779,  # Free Signals channel
        # Days: 0=Mon, 2=Wed, 4=Fri
        "days": [5],
        # "days": [0, 2, 4],
        # Set all_day=True to forward throughout the whole day on the days above
        "all_day": True,
        # Time window (ignored when all_day=True)
        "start_time": "17:00",
        "end_time": "20:00",
    },
]

# Validate required credentials
if not API_ID or not API_HASH or not PHONE_NUMBER:
    raise ValueError(
        "Missing required credentials! Please create a .env file with:\n"
        "- API_ID\n"
        "- API_HASH\n"
        "- PHONE_NUMBER\n"
        "See .env.example for template."
    )
