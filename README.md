# 📝 Full CI/CD Pipeline: Markdown Notes App

A production-grade, enterprise-ready CI/CD pipeline built around a Python Flask Markdown Notes application backed by PostgreSQL, Docker containerization, Ansible automation, and GitHub Actions workflows.

---

## 🏗️ Architecture & Pipeline Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                     DEV & CI PIPELINE (GitHub Actions)                            |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   Feature Branch                 Pull Request to 'staging'             GitHub Actions CI          |
|  [feature/search]  ───────────> [ PR #1: staging ] ─────────────────> [.github/workflows/ci.yml]  |
|                                                                                │                  |
|                                                                                ├─▶ 1. Flake8 Lint |
|                                                                                ├─▶ 2. Pytest (14) |
|                                                                                └─▶ 3. Build Docker|
|                                                                                       │           |
|                                                                                       ▼           |
|                                                                            Push to GHCR Registry  |
|                                                                          [:staging-{git-sha}]     |
+---------------------------------------------------------------------------------------┼-----------+
                                                                                        │
+---------------------------------------------------------------------------------------▼-----------+
|                                  STAGING CONTINUOUS DEPLOYMENT (CD)                               |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   Merge into 'staging'           Ansible Deployment                 Automated Smoke Test          |
|  [ staging branch ] ──────────> [ansible/deploy.yml] ─────────────> [GET :5001/health]           |
|          │                                                                 │                      |
|          ▼                                                   ┌─────────────┴─────────────┐        |
|  [update_changelog.py]                                       │                           │        |
|  Auto-appends CHANGELOG.md                                (Pass)                      (Fail)      |
|                                                              ▼                           ▼        |
|                                                      Staging Live (5001)        [ansible/rollback]|
|                                                                                 Auto-Revert Image |
+---------------------------------------------------------------------------------------------------+
                                                                                        │
+---------------------------------------------------------------------------------------▼-----------+
|                                    PRODUCTION RELEASE GATE                                        |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   Release PR to 'main'           Manual Approval Gate               Production Deployment         |
|  [ PR: staging -> main ] ─────> [environment: production] ───────> [.github/workflows/prod.yml]   |
|                                 (Requires Lead Sign-off)                     │                    |
|                                                                              ├─▶ Tag :v1.0.0      |
|                                                                              ├─▶ Tag :latest      |
|                                                                              └─▶ Deploy :5000     |
|                                                                                  (CPU/Mem Limits) |
+---------------------------------------------------------------------------------------------------+
```

---

## 🛠️ Technology Stack & Tools

| Tool | Purpose | Implementation Details |
| :--- | :--- | :--- |
| **Python 3.12** | Core Application | Flask 3.0.3, Application Factory pattern |
| **PostgreSQL 16** | Relational Database | SQLAlchemy 2.0 ORM, persistent named volume |
| **Mistune 3.0** | Markdown Engine | Renders headings, bold/italics, tables, code blocks |
| **Docker & Compose** | Containerization | Multi-stage Dockerfile, non-root user, compose overrides |
| **Pytest** | Testing Suite | 14 unit & integration tests, SQLite in-memory with StaticPool |
| **Flake8** | Static Analysis | Enforces PEP 8 compliance, fail-fast CI gate |
| **GitHub Actions** | CI/CD Engine | 3 distinct workflows: `ci.yml`, `staging.yml`, `production.yml` |
| **Ansible** | Orchestration & CD | Idempotent deployment, smoke tests, automatic rollback |
| **Ansible Vault** | Secrets Encryption | AES-256 encrypted production credentials (`vault/secrets.yml`) |
| **GHCR** | Container Registry | Tagged with `:staging-{sha}`, `:v1.0.0`, and `:latest` |

---

## 📂 Project Directory Structure

```
notes-app/
├── app/
│   ├── __init__.py           # Package initializer
│   ├── app.py                # Flask application factory, CRUD routes, /health check
│   ├── models.py             # Note database model & Mistune markdown rendering
│   └── templates/            # Jinja2 responsive dark-theme templates
│       ├── base.html         # Base layout, typography, navigation, CSS design tokens
│       ├── index.html        # Note card grid, search bar, CRUD action buttons
│       ├── create.html       # Markdown editor form with live syntax hints
│       ├── edit.html         # Note editor form
│       └── view.html         # Rendered Markdown view
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures (app, client, sample_note)
│   └── test_notes.py         # 14 automated unit and integration tests
├── scripts/
│   └── update_changelog.py   # Automated Conventional Commits changelog generator
├── ansible/
│   ├── deploy.yml            # Deployment playbook with retry smoke test & rescue block
│   └── rollback.yml          # Self-healing rollback playbook
├── vault/
│   ├── secrets.yml           # AES-256 Ansible Vault encrypted secrets (safe to commit)
│   └── secrets.example.yml   # Unencrypted reference template for developers
├── .github/
│   └── workflows/
│       ├── ci.yml            # PR Pipeline: lint -> test -> build image -> push GHCR
│       ├── staging.yml       # Staging CD: update changelog -> Ansible deploy -> smoke test
│       └── production.yml    # Production Gate: manual approval -> tag :v1.0.0 -> deploy
├── compose.staging.yml       # Staging Docker Compose override (Port 5001)
├── compose.prod.yml          # Production Docker Compose override (Port 5000 + limits)
├── docker-compose.yml        # Base multi-container service definition
├── Dockerfile                # Production non-root Docker build recipe
├── .dockerignore             # Excludes temp files from build context
├── .flake8                   # Linter style configuration
├── .gitignore                # Git exclusion rules
├── CHANGELOG.md              # Auto-growing release notes
├── requirements.txt          # Pinned dependencies
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Local Development Setup (Virtual Environment)
```powershell
# Create & activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run linter & test suite
flake8 .
pytest -v

# Start local development server
python -m app.app
```

### 2. Run with Docker Compose (Multi-Container)
```powershell
# Build and start Web + PostgreSQL stack in background
docker compose up --build -d

# Check running container health
docker compose ps

# Access Web UI in browser
http://localhost:5000
```

### 3. Run Staging Environment
```powershell
# Starts on port 5001
docker compose -f docker-compose.yml -f compose.staging.yml up -d --build
```

---

## 🛡️ Key DevOps Deliverables Verified

- [x] **Full CI/CD Pipeline Diagram**: Documented above in ASCII format.
- [x] **Automated Staging Deploy & Smoke Test**: Deploys on merge to `staging` and probes `/health` endpoint.
- [x] **Self-Healing Rollback**: Automatically reverts to the previous image tag if a smoke test fails.
- [x] **Ansible Vault Encrypted Secrets**: Production database passwords encrypted with AES-256 and committed safely.
- [x] **Automated CHANGELOG.md**: Automatically groups Conventional Commits into Features, Fixes, CI/CD, and Security.
- [x] **Semantic Version Tagging**: Production releases tagged `:v1.0.0` and `:latest`.
