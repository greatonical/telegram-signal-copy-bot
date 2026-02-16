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
        "target_topic_id": 242,  # Nova
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
        "target_topic_id": 259,  # Infinity Pips topic
    },
    {
        "source_id": -1002871747055,  # OBIOFLAGOS FX COMMUNITY
        "target_id": -1003621804175,  # OBI THE GOD FX community (Africa)
    },
    {
        "source_id": -1003108945324,  # Gilly Options Signals
        "target_id": -1003850746623,  # Binary Option signals
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

# Validate required credentials
if not API_ID or not API_HASH or not PHONE_NUMBER:
    raise ValueError(
        "Missing required credentials! Please create a .env file with:\n"
        "- API_ID\n"
        "- API_HASH\n"
        "- PHONE_NUMBER\n"
        "See .env.example for template."
    )
