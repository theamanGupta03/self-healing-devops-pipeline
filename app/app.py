import os
import time
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
START_TIME = time.time()


@app.route("/")
def home():
    logger.info("Home endpoint hit")
    return jsonify({
        "app": "Self-Healing DevOps Pipeline",
        "version": APP_VERSION,
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/health")
def health():
    uptime_seconds = int(time.time() - START_TIME)
    return jsonify({
        "status": "UP",
        "message": "Application is healthy",
        "version": APP_VERSION,
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@app.route("/info")
def info():
    return jsonify({
        "version": APP_VERSION,
        "env": os.getenv("FLASK_ENV", "production"),
        "hostname": os.uname().nodename,
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
