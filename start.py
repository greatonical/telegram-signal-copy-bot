"""
Startup script that runs both the Telegram bot and API server
"""

import asyncio
import logging
import os
import threading
from bot import main as bot_main
from api import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_api():
    """Run the Flask API server in a separate thread"""
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting API server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def run_bot():
    """Run the Telegram bot"""
    logger.info("Starting Telegram bot")
    asyncio.run(bot_main())


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("STARTING TELEGRAM SIGNAL COPY BOT WITH API SERVER")
    logger.info("=" * 80)

    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Run the bot in the main thread
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("\n✓ Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Service crashed: {e}", exc_info=True)
