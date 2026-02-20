# Token Trail - Setup Guide

This guide explains how to get Token Trail running locally with Docker Compose.

---

## Prerequisites

- **Docker** and **Docker Compose** installed and running
- **Git** (for cloning the repo)

Check Docker:
```bash
docker --version
docker compose version
```

---

## 1. Copy Environment Files

Create your `.env` file from the example:

**Linux / Mac:**
```bash
cp .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Optional (frontend):** If you run the frontend outside Docker, copy `frontend/.env.example` to `frontend/.env`:
```bash
cp frontend/.env.example frontend/.env
```

---

## 2. Run the Stack

From the project root:

```bash
docker compose up --build
```

This builds and starts:
- **mongodb** on port 27017
- **backend** (FastAPI) on port 8000
- **worker** (analysis placeholder)
- **frontend** (Vite dev server) on port 5173

---

## 3. Access the Application

| Service   | URL                     |
|-----------|-------------------------|
| Frontend  | http://localhost:5173   |
| Backend API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |
| ReDoc     | http://localhost:8000/redoc |

---

## 4. Verify It Works

1. Open http://localhost:5173 — you should see "Token Trail" and a health check JSON from the backend.
2. Open http://localhost:8000/docs — Swagger UI should load.
3. Call `GET /api/health` — should return `{"status":"ok","service":"token-trail-api"}`.

---

## Common Troubleshooting

### Ports already in use

If ports 27017, 8000, or 5173 are in use, either stop the conflicting service or change the ports in `docker-compose.yml`, for example:

```yaml
ports:
  - "8001:8000"  # map host 8001 to container 8000
```

### Docker not running

Ensure Docker Desktop (or the Docker daemon) is running. On Windows, start Docker Desktop from the Start menu.

### "Cannot connect to the Docker daemon"

- Linux: ensure your user is in the `docker` group, or run with `sudo`.
- Windows/Mac: start Docker Desktop and wait until it is fully ready.

### Frontend cannot reach backend

The frontend calls the API at `VITE_API_BASE_URL` (default: `http://localhost:8000/api`). Ensure:
- The backend container is running and port 8000 is mapped.
- You are not behind a firewall blocking localhost.

### Build fails

- Ensure you have enough disk space.
- Try a clean build: `docker compose down` then `docker compose build --no-cache`.

---

## Running Backend Outside Docker (optional)

If you run the FastAPI backend directly on your host machine (not inside a container), change the MongoDB URI so it points to `localhost` instead of the Docker service name:

```bash
# In your .env (or export before running)
MONGO_URI=mongodb://localhost:27017
```

Then start the backend manually:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## Stopping the Stack

```bash
docker compose down
```

To also remove the MongoDB volume:
```bash
docker compose down -v
```
