# 🔁 Self-Healing DevOps Pipeline

> 💬 **"Don't just deploy. Deploy, validate, monitor, recover, and notify — automatically."**

A **production-grade DevOps system** that containerizes a Python Flask application, automates the complete CI/CD lifecycle through a **5-stage GitHub Actions pipeline**, validates deployments with deep health checks, automatically recovers from application failures, sends real-time Slack notifications, and provides live observability on AWS EC2 — all triggered by a single `git push`.

---

## 🌍 Live Demo — Running on AWS EC2

| Service         | Public URL                       |
| --------------- | -------------------------------- |
| 🐍 Flask App    | `http://51.20.43.30:5000`        |
| ❤️ Health Check | `http://51.20.43.30:5000/health` |
| 📊 Prometheus   | `http://51.20.43.30:9090`        |
| 📈 Grafana      | `http://51.20.43.30:3000`        |
| 📦 cAdvisor     | `http://51.20.43.30:8080`        |

---

# 🚩 The Problem

Most CI/CD pipelines focus mainly on building and deploying an application.

When something breaks in production:

* ❌ Someone gets paged
* ❌ Someone logs in manually
* ❌ Someone restarts the container
* ❌ Nobody knows what the application was doing before it failed
* ❌ Notifications may arrive too late

### This project automates that entire recovery workflow.

---

# ✅ The Solution

| Problem                                   | What This Project Does                                   |
| ----------------------------------------- | -------------------------------------------------------- |
| Manual deployments are error-prone        | Automated 5-stage GitHub Actions CI/CD pipeline          |
| Works on my machine syndrome              | Multi-stage Docker build with pinned dependencies        |
| No validation after deployment            | Deep health checks validate endpoints and JSON responses |
| Application failures need manual recovery | Automatic container restart and health-check retry       |
| No production visibility                  | Prometheus + Grafana + cAdvisor                          |
| No immediate failure visibility           | Targeted Slack notifications for pipeline states         |

---

# ⚙️ 5-Stage CI/CD Pipeline

Every `git push` to `main` triggers the automated pipeline.

```text
                         ┌──────────────────────┐
                         │      Git Push        │
                         │       to main        │
                         └──────────┬───────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions                           │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🧪 Stage 1 — Lint & Test                              │  │
│  │                                                       │  │
│  │ • flake8 code quality checks                          │  │
│  │ • pytest — 6 tests                                    │  │
│  │ • pytest-cov coverage report                          │  │
│  │                                                       │  │
│  │ ❌ Failure → Pipeline stops                           │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │ ✅ Pass                         │
│                             ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🐳 Stage 2 — Build & Push                             │  │
│  │                                                       │  │
│  │ • Multi-stage Docker build                            │  │
│  │ • Build optimized production image                    │  │
│  │ • Push versioned images to GHCR                       │  │
│  │ • Docker layer caching                                │  │
│  │                                                       │  │
│  │ ⚡ Build time optimized: ~60s → ~10s                  │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │ ✅ Pass                         │
│                             ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🚀 Stage 3 — Deploy                                   │  │
│  │                                                       │  │
│  │ • Connect to AWS EC2                                  │  │
│  │ • Pull the new image from GHCR                        │  │
│  │ • Deploy the application container                    │  │
│  │ • Run the new application version                     │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │                                 │
│                             ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🩺 Stage 4 — Health Check + Self-Healing              │  │
│  │                                                       │  │
│  │ • Validate application endpoints                      │  │
│  │ • Validate JSON responses                             │  │
│  │ • Check application health                            │  │
│  │                                                       │  │
│  │ ❌ Health check fails                                 │  │
│  │        ↓                                              │  │
│  │ ♻️ Restart container                                  │  │
│  │        ↓                                              │  │
│  │ 🔄 Run health check again                             │  │
│  │        ↓                                              │  │
│  │ ✅ Recovered → Recovery notification                  │  │
│  │ 🚨 Failed → Escalation notification                   │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │                                 │
│                             ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 📣 Stage 5 — Slack Notification                       │  │
│  │                                                       │  │
│  │ • Pipeline success                                    │  │
│  │ • Test/lint failure                                   │  │
│  │ • Docker build/push failure                           │  │
│  │ • Self-healing recovery                               │  │
│  │ • Self-healing failure                                │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# 🧪 Stage 1 — Lint & Test

The first stage validates the application before building anything.

### Tools

* **flake8** → Code quality and style validation
* **pytest** → Automated application tests
* **pytest-cov** → Test coverage reporting

The pipeline stops immediately if linting or tests fail.

```text
Code Push
   ↓
flake8
   ↓
pytest
   ↓
Coverage
   ↓
✅ Pass → Stage 2
❌ Fail → Pipeline stops
```

The project currently contains **6 automated tests** covering application responses, JSON structure, health status, information endpoints, and invalid routes.

---

# 🐳 Stage 2 — Build & Push

After the code passes validation, GitHub Actions builds the Docker image.

### Docker build characteristics

* Multi-stage Docker build
* Pinned dependencies
* Non-root application user
* Production-ready Gunicorn server
* Docker layer caching

The resulting image is pushed to **GitHub Container Registry (GHCR)** with versioned tags.

### Why multi-stage Docker builds?

The build environment may require tools and dependencies that are not needed when the application actually runs.

Multi-stage builds allow the final image to contain only what is required to run the application.

**Result:**

```text
Smaller image
     ↓
Faster push
     ↓
Faster pull
     ↓
Faster deployment
```

---

# 🚀 Stage 3 — Deploy

Once the image is successfully pushed to GHCR, the deployment stage updates the application running on **AWS EC2**.

```text
GHCR
 │
 │ Pull new image
 ▼
AWS EC2
 │
 ▼
Docker Container
 │
 ▼
Flask Application
```

The deployed application is then passed to the health-check stage.

---

# 🩺 Stage 4 — Health Check + Self-Healing

This is the core feature that makes the pipeline **self-healing**.

The pipeline does not assume that a successful Docker deployment means the application is healthy.

Instead, it performs a **deep health validation**.

The health check validates:

* HTTP endpoint availability
* HTTP status
* JSON response structure
* Application status
* Application version

Example:

```text
GET /
→ status=running

GET /health
→ status=UP

GET /info
→ version=abc1234
```

### Self-Healing Flow

```text
Application deployed
        ↓
Health check
        ↓
   ┌────┴────┐
   │         │
  PASS      FAIL
   │         │
   ↓         ↓
Success   Restart container
             ↓
          Wait 10 sec
             ↓
        Health check again
             ↓
        ┌────┴────┐
        │         │
     Recovered   Failed
        │         │
        ↓         ↓
     Notify     Escalate
```

The project uses an automated recovery step that restarts the failed container and runs the health check again.

---

# 📣 Stage 5 — Slack Notifications

The final stage provides real-time visibility into the pipeline.

Different events generate different notifications.

| Event                      | Notification               |
| -------------------------- | -------------------------- |
| ✅ Pipeline succeeds        | Success notification       |
| ❌ Tests/lint fail          | Test failure notification  |
| 🐳 Docker build/push fails | Build failure notification |
| ♻️ Self-healing succeeds   | Recovery notification      |
| 🚨 Self-healing fails      | Critical alert             |

This means the team does not have to continuously monitor GitHub Actions.

---

# ♻️ Self-Healing Logic

When the health check fails:

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

The application is restarted automatically and validated again.

If the application recovers:

```text
♻️ Self-Healing Succeeded
```

If it does not recover:

```text
🚨 Self-Healing Failed
Manual Intervention Required
```

---

# 📊 Observability Stack

The application is monitored using:

* **Prometheus**
* **Grafana**
* **cAdvisor**

Four containers work together to provide application and infrastructure visibility.

```text
                    /metrics
                       │
                       ▼
┌──────────────┐   scrape   ┌───────────────┐
│  Flask App   │ ─────────► │  Prometheus   │
│    :5000     │            │     :9090     │
└──────────────┘            └───────┬───────┘
                                    │
                                    │ Data Source
                                    ▼
                            ┌───────────────┐
                            │    Grafana    │
                            │     :3000     │
                            └───────────────┘

┌──────────────┐
│   cAdvisor   │
│    :8080     │
└──────┬───────┘
       │
       │ Container metrics
       ▼
   Prometheus
```

### Grafana Dashboard

The dashboard provides metrics such as:

| Panel                  | What It Shows                 |
| ---------------------- | ----------------------------- |
| 🟢 HTTP Request Rate   | Requests per second           |
| 🔵 Request Latency p95 | 95th percentile response time |
| 🟡 App Uptime          | Application uptime            |
| 🟠 Container CPU       | Docker CPU usage              |

---

# 📁 Project Structure

```text
self-healing-devops-pipeline/
│
├── 📂 .github/workflows/
│   └── ci-cd.yml
│       └── 5-stage CI/CD pipeline
│
├── 📂 app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── 📂 tests/
│   └── test_app.py
│
├── 📂 scripts/
│   └── health_check.sh
│
├── 📂 monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       └── provisioning/
│
├── docker-compose.yml
└── README.md
```

---

# 🌐 API Endpoints

| Endpoint   | Method | Description                                     |
| ---------- | ------ | ----------------------------------------------- |
| `/`        | GET    | Application name, version, status and timestamp |
| `/health`  | GET    | Health status and uptime                        |
| `/info`    | GET    | Environment, hostname and version               |
| `/metrics` | GET    | Prometheus metrics                              |

### `/health` response

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

# 🚀 Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/theamanGupta03/self-healing-devops-pipeline.git
cd self-healing-devops-pipeline
```

## 2. Start all containers

```bash
docker-compose up --build -d
```

## 3. Verify containers

```bash
docker-compose ps
```

## 4. Check application health

```bash
curl http://localhost:5000/health
```

---

# 🔐 GitHub Secrets

The pipeline requires:

| Secret              | Description                           |
| ------------------- | ------------------------------------- |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL            |
| `GITHUB_TOKEN`      | GitHub-provided token for GHCR access |

---

# 🧪 Run Tests Locally

```bash
pip install -r app/requirements.txt pytest pytest-cov flake8
pytest tests/ -v --cov=app
```

Expected result:

```text
test_home_returns_200              PASSED
test_home_json_structure           PASSED
test_health_returns_200            PASSED
test_health_json_structure         PASSED
test_info_endpoint                 PASSED
test_nonexistent_route_returns_404 PASSED

6 passed
```

---

# 🔑 Key Engineering Decisions

### 🐳 Multi-stage Docker Build

Keeps unnecessary build dependencies out of the final production image.

### 👤 Non-root Container

The application runs as `appuser` instead of root, reducing container security risk.

### 📌 Pinned Dependencies

Dependencies use fixed versions to provide reproducible builds.

Example:

```text
flask==3.0.3
```

instead of:

```text
flask>=3
```

### ⚡ Gunicorn

Gunicorn is used instead of Flask's development server for production execution.

### 🔖 Git SHA Versioning

Each container identifies the exact Git commit/version being deployed.

### ⚡ Docker Layer Caching

Unchanged Docker layers are reused, reducing build time from approximately **60 seconds to 10 seconds**.

### 📣 Targeted Slack Notifications

Different pipeline failures and recovery scenarios generate different Slack notifications.

---

# 🗺️ Project Phases

* [x] Phase 1 — GitHub Actions CI/CD pipeline with self-healing
* [x] Phase 2 — Prometheus and Grafana observability
* [x] Phase 3 — Deployment to AWS EC2
* [x] Phase 4 — Slack alerts and recovery notifications

---

# 🧰 Tech Stack

| Category         | Technologies                                 |
| ---------------- | -------------------------------------------- |
| Application      | Python 3.12 · Flask 3.0.3 · Gunicorn         |
| Containerization | Docker · Docker Compose · Multi-stage builds |
| CI/CD            | GitHub Actions · GHCR                        |
| Testing          | pytest · flake8 · pytest-cov                 |
| Monitoring       | Prometheus · Grafana · cAdvisor              |
| Notifications    | Slack Incoming Webhooks                      |
| Cloud            | AWS EC2                                      |
| Scripting        | Bash · curl                                  |
| Version Control  | Git · GitHub                                 |

---

# 🎯 What Makes This Project Different?

This is not simply a **CI/CD deployment pipeline**.

It combines:

```text
Code
 ↓
Test
 ↓
Build
 ↓
Push
 ↓
Deploy
 ↓
Validate
 ↓
Detect Failure
 ↓
Recover Automatically
 ↓
Monitor
 ↓
Notify
```

The key engineering concept is:

> **The pipeline does not stop at deployment. It validates the running application and attempts automatic recovery when the deployment becomes unhealthy.**

---

# 👨‍💻 Author

**Aman Gupta**

Aspiring DevOps / Cloud Engineer

---

⭐ **If this project helped you, give it a star!**

*Built with real DevOps practices — not just tutorials.*
