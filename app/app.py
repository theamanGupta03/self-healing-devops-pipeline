import os
import time
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
START_TIME = time.time()

# ── Prometheus Metrics ─────────────────────────────────────────────
REQUEST_COUNT = Counter(
    'flask_request_count_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'flask_request_latency_seconds',
    'HTTP request latency',
    ['endpoint']
)
APP_UPTIME = Gauge(
    'flask_app_uptime_seconds',
    'Application uptime in seconds'
)


@app.before_request
def start_timer():
    from flask import g
    g.start = time.time()


@app.after_request
def record_metrics(response):
    from flask import g, request
    latency = time.time() - g.start
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    APP_UPTIME.set(time.time() - START_TIME)
    return response


@app.route("/")
def home():
    logger.info("Home endpoint hit")
    return "Hello World!"


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


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
