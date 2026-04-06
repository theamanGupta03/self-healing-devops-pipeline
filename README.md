# 🔁 Self-Healing DevOps Pipeline

> 💬 **"Don't just deploy. Deploy, validate, monitor, recover, and notify — automatically."**

A **production-grade DevOps system** that containerizes a Python Flask app, automates the entire CI/CD lifecycle, validates deployments with a deep health check, self-heals on failure, sends real-time Slack notifications, and provides live observability on AWS EC2 — all triggered by a single `git push`.

---

## 🌍 Live Demo — Running on AWS EC2

| Service | Public URL |
|---|---|
| 🐍 Flask App | http://13.51.238.154:5000 |
| ❤️ Health Check | http://13.51.238.154:5000/health |
| 📊 Prometheus | http://13.51.238.154:9090 |
| 📈 Grafana | http://13.51.238.154:3000 |
| 📦 cAdvisor | http://13.51.238.154:8080 |

---

## 🚩 The Problem

Most pipelines just build and deploy. When something breaks in production:

❌ Someone gets paged  
❌ Someone logs in manually  
❌ Someone restarts the container  
❌ Nobody knows what the app was doing before it broke  
❌ Nobody gets notified until it's too late  

**This project eliminates that entire chain.**

---

## ✅ The Solution

| Problem | What This Project Does |
|---|---|
| Manual deployments are error-prone | Fully automated 3-job GitHub Actions pipeline |
| Works on my machine syndrome | Multi-stage Docker build with pinned dependencies |
| No validation after deployment | Deep health check validates every endpoint and JSON response |
| Failures need manual recovery | Container auto-restarts and re-validates without human input |
| No visibility into production | Prometheus + Grafana live metrics on AWS EC2 |
| Nobody knows when it breaks | Slack notifications for every pipeline state |

---

## ⚙️ How The Pipeline Works

Every `git push` to `main` triggers this sequence — fully automatic, no human steps:

```
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Actions                             │
│                                                                 │
│   📦 Push Code                                                  │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────┐                               │
│   │  🧪  Stage 1 — Lint & Test  │                               │
│   │  • flake8 code style check  │                               │
│   │  • pytest — 6 tests         │                               │
│   │  • coverage report upload   │                               │
│   │  ❌ Fails? Pipeline stops.  │                               │
│   └──────────────┬──────────────┘                               │
│                  │ ✅ Pass                                       │
│                  ▼                                               │
│   ┌──────────────────────────────────┐                          │
│   │  🐳  Stage 2 — Build & Push      │                          │
│   │  • Multi-stage Docker build      │                          │
│   │  • Push to GHCR (3 image tags)   │                          │
│   │  • Layer caching — 60s to 10s    │                          │
│   └──────────────┬───────────────────┘                          │
│                  │ ✅ Pass                                       │
│                  ▼                                               │
│   ┌──────────────────────────────────────────────┐              │
│   │  🩺  Stage 3 — Health Check + Self-Healing   │              │
│   │  • Pull image → Run container                │              │
│   │  • Validate all endpoints + JSON             │              │
│   │  • ❌ Fails? → Restart → Retry               │              │
│   │  • ♻️ Recovered? → Slack notify              │              │
│   │  • 🚨 Still failing? → Slack escalate        │              │
│   └──────────────┬───────────────────────────────┘              │
│                  │ always                                        │
│                  ▼                                               │
│   ┌──────────────────────────────────────────────┐              │
│   │  📣  Stage 4 — Slack Notification            │              │
│   │  • ✅ All passed → green notification        │              │
│   │  • ❌ Tests failed → red notification        │              │
│   │  • 🐳 Build failed → orange notification     │              │
│   │  • 🚨 Self-healing failed → dark red alert   │              │
│   └──────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Self-Healing Logic

When the health check fails, this runs automatically:

```yaml
- name: 🔄 Self-Healing
  if: failure() && steps.healthcheck.conclusion == 'failure'
  id: selfhealing
  run: |
    echo "Restarting container..."
    docker restart self-healing-app
    sleep 10
    ./scripts/health_check.sh && echo "✅ Recovered!" || exit 1
```

The script validates not just the HTTP status code, but also the JSON response body:

```
✅ PASS — Endpoint /        → status=running
✅ PASS — Endpoint /health  → status=UP
✅ PASS — Endpoint /info    → version=abc1234
```

---

## 📣 Slack Notifications

5 targeted notifications — each fires for a specific scenario:

| Emoji | Trigger | Color |
|---|---|---|
| ✅ | All jobs pass | Green |
| ❌ | Tests or lint fail | Red |
| 🐳 | Docker build/push fails | Orange |
| ♻️ | Self-healing recovers the app | Green |
| 🚨 | Self-healing fails — manual fix needed | Dark Red |

**Example failure message in Slack:**
```
🚨 Self-Healing Failed — Manual Intervention Required!

Failed Job   → 🩺 Health Check & Self-Healing
Branch       → main
Commit       → abc1234
Triggered by → theamanGupta03
Reason       → App failed health checks and could not auto-recover
Run          → https://github.com/.../actions/runs/...
```

**Example recovery message:**
```
♻️ Self-Healing Succeeded — App Recovered!

Repository   → theamanGupta03/self-healing-devops-pipeline
Branch       → main
Action Taken → App failed initial health check but recovered
               automatically after container restart
Run          → https://github.com/.../actions/runs/...
```

---

## 📊 Observability Stack

Four containers work together to give complete visibility:

```
┌──────────────┐     scrapes every 15s    ┌─────────────────┐
│  Flask App   │ ──────────────────────►  │   Prometheus    │
│  :5000       │      /metrics            │   :9090         │
└──────────────┘                          └────────┬────────┘
                                                   │ data source
┌──────────────┐     scrapes every 15s             │
│  cAdvisor    │ ──────────────────────►  ┌────────▼────────┐
│  :8080       │   container CPU/memory   │    Grafana      │
└──────────────┘                          │    :3000        │
                                          └─────────────────┘
```

### 📈 Live Grafana Dashboard Panels

| Panel | What It Shows |
|---|---|
| 🟢 HTTP Request Rate | Requests per second per endpoint and status code |
| 🔵 Request Latency p95 | 95th percentile response time |
| 🟡 App Uptime | Seconds since last start — resets to 0 if app crashes |
| 🟠 Container CPU | Docker CPU usage over time |

---

## 📁 Project Structure

```
self-healing-devops-pipeline/
│
├── 📂 .github/workflows/
│   └── ci-cd.yml              ← 4-job pipeline with self-healing + Slack
│
├── 📂 app/
│   ├── app.py                 ← Flask: /, /health, /info, /metrics
│   ├── requirements.txt       ← Pinned versions
│   └── Dockerfile             ← Multi-stage build, non-root user
│
├── 📂 tests/
│   └── test_app.py            ← 6 tests: status codes + JSON structure
│
├── 📂 scripts/
│   └── health_check.sh        ← Deep validator + self-healing trigger
│
├── 📂 monitoring/
│   ├── prometheus.yml         ← Scrape config: Flask + cAdvisor
│   └── grafana/provisioning/  ← Auto-configures datasource + dashboard
│
├── docker-compose.yml         ← Runs all 4 containers with one command
└── README.md
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | App name, version, status, timestamp |
| `/health` | GET | Health status + uptime — used by pipeline |
| `/info` | GET | Environment, hostname, version |
| `/metrics` | GET | Prometheus metrics — scraped every 15 seconds |

**`/health` response:**
```json
{
  "status": "UP",
  "message": "Application is healthy",
  "version": "abc1234",
  "uptime_seconds": 946,
  "timestamp": "2026-04-06T02:38:09+00:00"
}
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/theamanGupta03/self-healing-devops-pipeline.git
cd self-healing-devops-pipeline

# 2. Start all 4 containers
docker-compose up --build -d

# 3. Verify everything is healthy
docker-compose ps

# 4. Hit the health endpoint
curl http://localhost:5000/health
```

**Open in browser:**

| Service | URL | Credentials |
|---|---|---|
| Flask App | http://localhost:5000 | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / admin123 |
| cAdvisor | http://localhost:8080 | — |

---

## 🔐 GitHub Secrets Required

| Secret | Description |
|---|---|
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL for notifications |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions for GHCR access |

**Setting up Slack Webhook:**
1. Go to your Slack workspace → Apps → Incoming Webhooks
2. Click Add to channel → select your channel
3. Copy the webhook URL
4. GitHub repo → Settings → Secrets and variables → Actions → New secret

---

## 🧪 Run Tests Locally

```bash
pip install -r app/requirements.txt pytest pytest-cov flake8
pytest tests/ -v --cov=app
```

```
test_home_returns_200              PASSED
test_home_json_structure           PASSED
test_health_returns_200            PASSED
test_health_json_structure         PASSED
test_info_endpoint                 PASSED
test_nonexistent_route_returns_404 PASSED

6 passed in 0.08s ✅
```

---

## 🔑 Key Engineering Decisions

**🐳 Multi-stage Docker build** — No pip or build tools in the final image. Smaller, more secure.

**👤 Non-root container user** — App runs as `appuser`. No root-level damage if compromised.

**📌 Pinned dependency versions** — `flask==3.0.3` not `flask>=3`. Same environment every build.

**⚡ Gunicorn over Flask dev server** — 2 workers, 60s timeout, production-ready.

**🔖 Git SHA as APP_VERSION** — Every container knows exactly what code it's running.

**⚡ GitHub Actions layer caching** — Unchanged Docker layers reused. 60s → 10s builds.

**📣 Targeted Slack notifications** — Each failure scenario has its own message and color. No generic alerts.

---

## 🗺️ Roadmap

- [x] ✅ Phase 1 — GitHub Actions CI/CD pipeline with self-healing
- [x] ✅ Phase 2 — Prometheus and Grafana observability stack
- [x] ✅ Phase 3 — Deployed to AWS EC2 — Live at `13.51.238.154`
- [x] ✅ Phase 4 — Slack alerts for all pipeline states + recovery notifications
- [ ] 🔲 Phase 5 — Trivy Docker image security scanning
- [ ] 🔲 Phase 6 — Staging and production environments with approval gate

---

## 🧰 Tech Stack

| Category | Technologies |
|---|---|
| Application | Python 3.12 · Flask 3.0.3 · Gunicorn |
| Containerization | Docker (multi-stage) · Docker Compose |
| CI/CD | GitHub Actions · GHCR |
| Testing | pytest · flake8 · pytest-cov |
| Monitoring | Prometheus · Grafana · cAdvisor · prometheus-client |
| Notifications | Slack Incoming Webhooks |
| Cloud | AWS EC2 |
| Scripting | Bash · curl |
| Version Control | Git · GitHub |

---

## 👨‍💻 Author

**Aman Gupta** — Aspiring DevOps / Cloud Engineer




⭐ **If this project helped you, give it a star!** ⭐

*Built with real DevOps practices — not just tutorials.*

