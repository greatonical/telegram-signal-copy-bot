"""
Simple API server for health checks and cronjob monitoring
"""

import logging
from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring and cronjobs"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "telegram-signal-copy-bot",
        }
    ), 200


@app.route("/ping", methods=["GET"])
def ping():
    """Simple ping endpoint"""
    return jsonify({"message": "pong"}), 200


@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API info"""
    return jsonify(
        {
            "service": "Telegram Signal Copy Bot API",
            "version": "1.0.0",
            "endpoints": {
                "/health": "Health check endpoint",
                "/ping": "Simple ping endpoint",
            },
        }
    ), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting API server on port {port}")
    app.run(host="0.0.0.0", port=port)
