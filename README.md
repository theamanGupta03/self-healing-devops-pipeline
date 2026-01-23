# Self-Healing DevOps Pipeline

## 📌 Overview
This project demonstrates a **production-oriented DevOps workflow** where a Python Flask application is containerized using Docker and prepared for CI/CD automation and self-healing mechanisms.

The objective is not just application deployment, but building a **reliable, observable, and automation-ready system**, aligned with real-world DevOps practices.

---

## 🎯 Problem Statement
Traditional deployments often suffer from:
- Manual build and deployment processes
- Environment inconsistencies ("works on my machine")
- No automated health validation
- No recovery mechanism during failures

This project addresses these challenges by:
- Containerizing the application
- Introducing a health check endpoint
- Preparing the foundation for CI/CD and self-healing automation

---

## 🏗️ Architecture (Current Phase)

```
Developer
   |
   v
GitHub Repository
   |
   v
Jenkins (CI/CD)
   |
   v
Docker Build
   |
   v
Docker Container
   |
   v
Flask Application (/health)
```

---

## 🧰 Tech Stack

| Category | Technology |
|--------|-----------|
| Programming Language | Python |
| Web Framework | Flask |
| Containerization | Docker |
| CI/CD | Jenkins |
| Version Control | Git |
| Repository Hosting | GitHub |
| OS Environment | Linux (Ubuntu via WSL2) |

---

## 📁 Project Structure

```
self-healing-devops-pipeline/
│
├── app/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Docker build instructions
│
├── .gitignore
└── README.md
```

---

## 🚀 Application Details

### Endpoints

| Endpoint | Method | Description |
|--------|--------|-------------|
| `/` | GET | Application home |
| `/health` | GET | Health check endpoint |

### Sample `/health` Response

```json
{
  "status": "UP",
  "message": "Application is healthy"
}
```

The `/health` endpoint is lightweight and designed for:
- CI/CD validation
- Container health checks
- Self-healing logic

---

## 🐳 Docker Implementation

### Build Docker Image
```bash
docker build -t self-healing-app ./app
```

### Run Docker Container
```bash
docker run -p 5000:5000 self-healing-app
```

### Access the Application
- http://localhost:5000/
- http://localhost:5000/health

---

## ✅ Validation Performed
- Application tested locally
- Docker image built successfully
- Container runtime validated
- Health endpoint verified from inside the container

---

## 🔄 CI/CD & Self-Healing (Planned)

- Jenkins CI/CD pipeline
  - Pull code from GitHub
  - Build Docker image
  - Run container
  - Fail pipeline if `/health` check fails

- Self-healing logic
  - Automatic container restart on failure
  - Redeploy last stable image

---

## 💡 Why This Project Matters
This project goes beyond basic deployments by focusing on:
- Automation readiness
- Health-based validation
- Production-aligned DevOps workflows

It demonstrates **DevOps thinking**, not just tool usage.

---

## 👨‍💻 Author
**Aman Gupta**  
Aspiring DevOps / Cloud Engineer

---

## 📌 License
This project is for learning and demonstration purposes.
