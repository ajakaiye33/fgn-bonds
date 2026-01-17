# Deployment Guide for FGN Savings Bond Application

This guide provides detailed instructions for deploying the FGN Savings Bond application in various environments.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
   - [AWS](#aws)
   - [Azure](#azure)
   - [Google Cloud](#google-cloud)
4. [Local Development](#local-development)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Backup and Restore](#backup-and-restore)
8. [Monitoring](#monitoring)

---

## Architecture Overview

The application uses a modern React + FastAPI architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                         NGINX                                │
│                    (Port 80 - Reverse Proxy)                │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   │
┌─────────────────┐  ┌─────────────────┐         │
│    Frontend     │  │     Backend     │         │
│   (React SPA)   │  │    (FastAPI)    │         │
│   Port 3000     │  │   Port 8000     │         │
│                 │  │                 │         │
│  - Form Wizard  │  │  - REST API     │         │
│  - Admin UI     │  │  - PDF Gen      │         │
│  - Charts       │  │  - Auth (JWT)   │         │
└─────────────────┘  └────────┬────────┘         │
                              │                   │
                              ▼                   │
                    ┌─────────────────┐          │
                    │     SQLite      │◄─────────┘
                    │   (Database)    │
                    └─────────────────┘
```

**Components:**
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + ReportLab (PDF)
- **Database**: SQLite (file-based, portable)
- **Proxy**: Nginx reverse proxy

---

## Docker Deployment

The application is containerized using Docker with **multi-stage builds** for optimized images.

### Prerequisites

- Docker Engine (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- Port 80 available

### Docker Image Architecture

Both frontend and backend use multi-stage Dockerfiles:

**Frontend Stages:**
| Stage | Base Image | Purpose |
|-------|------------|---------|
| `deps` | node:20-alpine | Install npm dependencies |
| `test` | node:20-alpine | Run tests, lint, type-check (has Node.js) |
| `build` | node:20-alpine | Compile TypeScript, bundle assets |
| `production` | nginx:alpine | Serve static files (~25MB) |

**Backend:**
| Stage | Base Image | Purpose |
|-------|------------|---------|
| Single | python:3.12-slim | Full application with all dependencies |

The frontend production image is **nginx-only** (no Node.js) for minimal size. To run frontend tests via Docker, use the `test` stage target.

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fgnbond_sub
   ```

2. Create the backend environment file:
   ```bash
   cp backend/.env.example backend/.env
   ```

3. Edit `backend/.env` with your configuration (see [Environment Variables](#environment-variables))

4. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```

5. Verify the application is running:
   ```bash
   docker-compose ps
   ```

6. Access the application:

   | Service | URL | Purpose |
   |---------|-----|---------|
   | User Form | http://localhost | Bond subscription wizard |
   | Admin Dashboard | http://localhost/admin | Analytics & management |
   | API Docs | http://localhost/api/docs | OpenAPI documentation |

---

## Cloud Deployment

### AWS

#### Using Elastic Container Service (ECS)

1. Create an ECR repository:
   ```bash
   aws ecr create-repository --repository-name fgn-bond-frontend
   aws ecr create-repository --repository-name fgn-bond-backend
   ```

2. Authenticate Docker to your ECR registry:
   ```bash
   aws ecr get-login-password | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<region>.amazonaws.com
   ```

3. Build, tag, and push the Docker images:
   ```bash
   # Frontend
   docker build -t fgn-bond-frontend ./frontend
   docker tag fgn-bond-frontend:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/fgn-bond-frontend:latest
   docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/fgn-bond-frontend:latest

   # Backend
   docker build -t fgn-bond-backend ./backend
   docker tag fgn-bond-backend:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/fgn-bond-backend:latest
   docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/fgn-bond-backend:latest
   ```

4. Create an ECS cluster, task definitions, and services using AWS Console or CLI.

5. Configure environment variables in the backend task definition.

6. Set up Application Load Balancer for routing.

#### Using Elastic Beanstalk

1. Install the EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize EB application:
   ```bash
   eb init -p docker fgn-bond-app
   ```

3. Create an environment:
   ```bash
   eb create fgn-bond-production
   ```

4. Deploy the application:
   ```bash
   eb deploy
   ```

### Azure

#### Using Azure Container Apps

1. Create an Azure Container Registry:
   ```bash
   az acr create --resource-group myResourceGroup --name fgnbondregistry --sku Basic
   ```

2. Build and push the images:
   ```bash
   az acr build --registry fgnbondregistry --image fgn-bond-frontend:latest ./frontend
   az acr build --registry fgnbondregistry --image fgn-bond-backend:latest ./backend
   ```

3. Create Container Apps:
   ```bash
   az containerapp create \
     --name fgn-bond-app \
     --resource-group myResourceGroup \
     --environment myContainerAppEnv \
     --image fgnbondregistry.azurecr.io/fgn-bond-frontend:latest \
     --target-port 3000 \
     --ingress external
   ```

### Google Cloud

#### Using Cloud Run

1. Build and push images to Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/fgn-bond-frontend ./frontend
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/fgn-bond-backend ./backend
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy fgn-bond-backend \
     --image gcr.io/[PROJECT_ID]/fgn-bond-backend \
     --platform managed \
     --allow-unauthenticated

   gcloud run deploy fgn-bond-frontend \
     --image gcr.io/[PROJECT_ID]/fgn-bond-frontend \
     --platform managed \
     --allow-unauthenticated
   ```

---

## Local Development

### Backend Setup

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access the development app at http://localhost:5173

---

## Running Tests

### Local Testing

```bash
# Frontend tests
cd frontend
npm run test:run          # Run once
npm run test              # Watch mode
npm run test:coverage     # With coverage report

# Backend tests
cd backend
source venv/bin/activate
pytest tests/ -v                              # Run all tests
pytest tests/ -v --cov=app --cov-report=html  # With coverage
pytest tests/test_auth.py -v                  # Specific file
```

### Docker Testing

The frontend has a dedicated test service that builds the `test` stage:

```bash
# Frontend tests via Docker
docker-compose --profile test run --rm frontend-test

# Or build and run manually
docker build --target test -t frontend-test ./frontend
docker run --rm frontend-test

# Backend tests via Docker
docker-compose run --rm backend pytest tests/ -v

# With coverage
docker-compose run --rm backend pytest tests/ -v --cov=app
```

### CI/CD Pipeline

GitHub Actions runs automatically on push/PR:

1. **Backend Job**: flake8, black, isort checks, then pytest
2. **Frontend Job**: ESLint, TypeScript check, Vitest, build
3. **Docker Job**: Validate compose, build images, health check

See `.github/workflows/ci.yml` for full configuration.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite connection string | `sqlite:///./data/fgn_bonds.db` |
| `ADMIN_USERNAME` | Admin login username | `admin` |
| `ADMIN_PASSWORD_HASH` | bcrypt hash of password | Hash of `admin123` |
| `JWT_SECRET_KEY` | Secret for JWT tokens | (generate unique) |
| `CORS_ORIGINS` | Allowed frontend origins | `["http://localhost:3000"]` |

### Generating Secure Values

**Generate JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Generate Admin Password Hash:**
```bash
python -c "import bcrypt; print(bcrypt.hashpw('YourPassword'.encode(), bcrypt.gensalt()).decode())"
```

---

## Database Setup

### SQLite (Default)

SQLite requires no external setup. The database file is created automatically at `backend/data/fgn_bonds.db`.

**Database Location:**
- Docker: `/app/data/fgn_bonds.db` (inside container)
- Local: `backend/data/fgn_bonds.db`

### Database Schema

Tables are created automatically by SQLAlchemy on first run:
- `applications` - Bond subscription applications
- `payments` - Payment records
- `documents` - Payment evidence uploads
- `dmo_submissions` - DMO report submission history

---

## Backup and Restore

### SQLite Backup

**Create a backup:**
```bash
# Docker
docker cp fgnbond_sub-backend-1:/app/data/fgn_bonds.db ./backup_$(date +%Y%m%d).db

# Local
cp backend/data/fgn_bonds.db ./backup_$(date +%Y%m%d).db
```

**Restore from backup:**
```bash
# Docker
docker cp ./backup_20260115.db fgnbond_sub-backend-1:/app/data/fgn_bonds.db
docker-compose restart backend

# Local
cp ./backup_20260115.db backend/data/fgn_bonds.db
```

### Automated Backups

Set up a cron job for regular backups:
```bash
# Daily backup at 2 AM
0 2 * * * docker cp fgnbond_sub-backend-1:/app/data/fgn_bonds.db /backup/fgn_bonds_$(date +\%Y\%m\%d).db
```

---

## Monitoring

### Application Logs

**View all service logs:**
```bash
docker-compose logs -f
```

**View specific service logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Health Check

**API Health:**
```bash
curl http://localhost/api/health
```

**Expected response:**
```json
{"status": "healthy"}
```

### Container Status

```bash
docker-compose ps
```

### Resource Usage

```bash
docker stats
```

---

## Troubleshooting

### Services Not Starting

```bash
# Check container status
docker-compose ps

# View logs for errors
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
```

### Database Issues

```bash
# Reset database (WARNING: deletes all data)
docker exec fgnbond_sub-backend-1 rm -f /app/data/fgn_bonds.db
docker-compose restart backend
```

### Port Conflicts

If port 80 is in use:
```bash
# Find process using port 80
lsof -i :80

# Or modify docker-compose.yml to use a different port
# Change "80:80" to "8080:80"
```

### Rebuild Containers

```bash
docker-compose down
docker-compose up -d --build
```
