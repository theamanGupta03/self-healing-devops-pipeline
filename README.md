
# Self-Healing Devops Pipleine.

A **production-grade DevOps system** that containerizes a Python Flask app, automates the entire CI/CD lifecycle, validates deployments with a deep health check, self-heals on failure, and provides real-time observability — all triggered by a single `git push`.

---

## 🚩 The Problem

Most pipelines just build and deploy. When something breaks in production:

❌ Someone gets paged  
❌ Someone logs in manually  
❌ Someone restarts the container  
❌ Nobody knows what the app was doing before it broke  

**This project eliminates that entire chain.**

---

## ✅ The Solution

| Problem | What This Project Does |
|---|---|
| Manual deployments are error-prone | Fully automated 4-job GitHub Actions pipeline |
| "Works on my machine" syndrome | Multi-stage Docker build with pinned dependencies |
| No validation after deployment | Deep health check — validates HTTP status + JSON on every endpoint |
| Failures need manual recovery | Self-healing — container auto-restarts and re-validates automatically |
| No visibility into production | Prometheus + Grafana — request rate, latency, uptime, CPU live |
| Nobody knows when pipeline fails | Slack alerts — commit, branch, run link sent instantly |

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
│   │  • Layer caching — 60s → 10s     │                          │
│   └──────────────┬───────────────────┘                          │
│                  │ ✅ Pass                                       │
│                  ▼                                               │
│   ┌──────────────────────────────────────────────┐              │
│   │  🩺  Stage 3 — Health Check + Self-Healing   │              │
│   │  • Pull image from GHCR                      │              │
│   │  • Run container                             │              │
│   │  • Validate all endpoints + JSON responses   │              │
│   │  • ❌ Fails? → Auto-restart → Retry once     │              │
│   │  • Still fails? Pipeline fails with logs     │              │
│   └──────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Self-Healing Logic

When the health check fails, this runs automatically:

```yaml
- name: 🔄 Self-Healing
  if: failure() && steps.healthcheck.conclusion == 'failure'
  run: |
    echo "Restarting container..."
    docker restart self-healing-app
    sleep 10
    ./scripts/health_check.sh && echo "✅ Recovered!" || exit 1
```

The script validates not just the HTTP status code, but also the JSON response body on every endpoint:

## 📣 Slack Notification Logic
```
- name: Notify Success
  if: all jobs passed
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
    --data '{ "text": "✅ Pipeline PASSED", ... }'

- name: Notify Failure  
  if: any job failed
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
    --data '{ "text": "❌ Pipeline FAILED", ... }'
✅ PASS — Endpoint /        → status=running
✅ PASS — Endpoint /health  → status=UP
✅ PASS — Endpoint /info    → version=abc1234

```
# What the Slack message includes:

✅ or ❌ status
Repository name
Branch
Commit SHA
Who triggered it
Direct link to the run

---

## 📊 Observability Stack

Four containers work together to give complete visibility:

```
┌──────────────┐     scrapes every 15s    ┌─────────────────┐
│  Flask App   │ ──────────────────────►  │   Prometheus    │
│  :5000       │      /metrics            │   :9090         │
│              │                          │  (time-series)  │
└──────────────┘                          └────────┬────────┘
                                                   │
┌──────────────┐     scrapes every 15s             │ data source
│  cAdvisor    │ ──────────────────────►           │
│  :8080       │   container CPU/memory  ┌────────▼────────┐
│ (Docker stats│                         │    Grafana      │
│  collector)  │                         │    :3000        │
└──────────────┘                         │  (dashboards)   │
                                         └─────────────────┘
```

### 📈 Live Grafana Dashboard Panels

| Panel | What It Shows |
|---|---|
| 🟢 HTTP Request Rate | Requests per second per endpoint and status code |
| 🔵 Request Latency p95 | 95th percentile response time — spikes mean slowdowns |
| 🟡 App Uptime | Seconds since last start — resets to 0 if the app crashes |
| 🟠 Container CPU | Docker CPU usage over time — spikes mean heavy processing |

---

## 📁 Project Structure

```
self-healing-devops-pipeline/
│
├── 📂 .github/workflows/
│   └── ci-cd.yml              ← The entire pipeline in one file
│
├── 📂 app/
│   ├── app.py                 ← Flask app: /, /health, /info, /metrics
│   ├── requirements.txt       ← Pinned versions — no surprise updates
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
| `/health` | GET | Health status + uptime — used by the pipeline |
| `/info` | GET | Environment, hostname, version |
| `/metrics` | GET | Prometheus metrics — scraped every 15 seconds |

**`/health` response:**
```json
{
  "status": "UP",
  "message": "Application is healthy",
  "version": "abc1234",
  "uptime_seconds": 102039,
  "timestamp": "2026-04-04T08:45:25+00:00"
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

## 🧪 Run Tests Locally

```bash
pip install -r app/requirements.txt pytest pytest-cov flake8
pytest tests/ -v --cov=app
```

```
tests/test_app.py::test_home_returns_200              PASSED
tests/test_app.py::test_home_json_structure           PASSED
tests/test_app.py::test_health_returns_200            PASSED
tests/test_app.py::test_health_json_structure         PASSED
tests/test_app.py::test_info_endpoint                 PASSED
tests/test_app.py::test_nonexistent_route_returns_404 PASSED

6 passed in 0.08s ✅
```

---

## 🔑 Key Engineering Decisions

**🐳 Multi-stage Docker build**
Dependencies install in a builder stage. Only the compiled packages copy into the final image — no pip, no build tools, no cache in production. Smaller image, smaller attack surface.

**👤 Non-root container user**
The app runs as `appuser`, not root. If the container is ever compromised, the attacker cannot escalate to root-level access.

**📌 Pinned dependency versions**
`flask==3.0.3` not `flask>=3`. Every build uses the exact same packages. No surprises from upstream library updates.

**⚡ Gunicorn over Flask dev server**
Flask's built-in server is single-threaded. Gunicorn runs with 2 worker processes and a 60-second timeout — production-ready.

**🔖 Git SHA as APP_VERSION**
The pipeline injects the exact commit hash as `APP_VERSION` at runtime. Every running container knows exactly what code it is running.

**⚡ GitHub Actions layer caching**
`cache-from: type=gha` reuses unchanged Docker layers. If only `app.py` changed, dependencies don't reinstall — builds go from 60s to 10s.

**⚡ Slack webhook over email**
instant, structured, actionable. Includes the run link so you can jump directly to the failed job.

---

## 🗺️ Roadmap

- [x] ✅ Phase 1 — GitHub Actions CI/CD pipeline with self-healing
- [x] ✅ Phase 2 — Prometheus and Grafana observability stack
- [x] ✅ Phase 3 — Deployed to AWS EC2 — Live at `13.220.176.117`
- [x] ✅ Phase 4 — Slack alerts on every pipeline run


---

## 🧰 Tech Stack

| Category | Technology | Purpose |
|---|---|---|
| Language | Python 3.12 | Application development |
| Web Framework | Flask 3.0.3 | REST API endpoints |
| WSGI Server | Gunicorn 22.0.0 | Production HTTP server |
| Containerization | Docker multi-stage | Portable, secure packaging |
| CI/CD | GitHub Actions | 4-job automated pipeline |
| Registry | GHCR | Docker image hosting with 3 tags |
| Testing | pytest + flake8 | Unit tests + linting |
| Metrics | prometheus-client | Expose app metrics at /metrics |
| Monitoring | Prometheus | Scrape + store time-series data |
| Visualization | Grafana | Live dashboards |
| Container Stats | cAdvisor | CPU, memory, network metrics |
| Self-Healing | Bash + curl | Health validation + auto-restart |
| Alerting | Slack Webhooks | Real-time pipeline notifications |
| Cloud | AWS EC2 | Live deployment |
| Orchestration | Docker Compose | Multi-container local stack |

## 👨‍💻 Author

**Aman Gupta** — Aspiring DevOps / Cloud Engineer

⭐ **If this project helped you, give it a star!** ⭐

*Built with real DevOps practices — not just tutorials.*

