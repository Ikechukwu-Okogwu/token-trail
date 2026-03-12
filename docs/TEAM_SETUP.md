# Token Trail — Team Setup & Project Guide

This is the single document every teammate should read before writing code.
It covers local setup, a full end-to-end walkthrough, what each file does, and how we work together.

> If you don't have the required `.env` values, ask the repo owner — we only commit `.env.example` to keep secrets out of Git.

---

## 1) Quick Start (Docker)

### Both (Docker + shared env)

**Prerequisites**

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running (Windows or Mac).
  Linux users: install Docker Engine + the Compose plugin.
- Git (for cloning the repo).

Verify Docker is ready:

```bash
docker --version
docker compose version
```

**Copy environment files**

Mac / Linux:
```bash
cp .env.example .env
```

Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

The defaults in `.env.example` work out of the box with Docker Compose. You don't need to change anything for local dev.

**Start the entire stack**

From the repo root:

```bash
docker compose up --build
```

First run downloads images and installs dependencies — it takes a few minutes. Subsequent runs are fast.

**What starts**

| Service | Container name | URL |
|---------|---------------|-----|
| MongoDB 7 | `token-trail-mongodb` | `localhost:27017` |
| FastAPI backend | `token-trail-backend` | http://localhost:8000 |
| Analysis worker | `token-trail-worker` | *(no port — runs in background)* |
| React + Vite frontend | `token-trail-frontend` | http://localhost:5173 |

### Backend (API + Worker + Mongo)

The backend and worker containers both mount `./backend:/app` so your local Python code changes are reflected inside the containers immediately. Uploads persist at `./uploads:/app/uploads` on both.

If you want to run the backend **outside** Docker (e.g. for a debugger), set this in your `.env`:

```
MONGO_URI=mongodb://localhost:27017
```

Then:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

You still need MongoDB running — either via Docker (`docker compose up mongodb`) or a local install.

### Frontend (React app)

The frontend container mounts `./frontend:/app` for live Vite hot-module replacement. If you want to run it outside Docker instead:

```bash
cd frontend
npm install
npm run dev
```

The dev server reads `VITE_API_BASE_URL` from `frontend/.env` (default: `http://localhost:8000/api`). Copy the example if you haven't:

Mac / Linux:
```bash
cp frontend/.env.example frontend/.env
```

Windows PowerShell:
```powershell
Copy-Item frontend\.env.example frontend\.env
```

---

## 2) Verify Everything Works (Smoke Tests)

### Backend (API + Worker + Mongo)

**Health check** — the first thing to try:

Mac / Linux:
```bash
curl http://localhost:8000/api/health
```

Windows PowerShell:
```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

Expected response:

```json
{ "status": "ok", "service": "token-trail-api" }
```

If this fails, the backend isn't running. Check logs: `docker compose logs -f backend`.

**Swagger UI** — open in your browser:

```
http://localhost:8000/docs
```

You should see every endpoint listed with "Try it out" buttons. The lock icon means that endpoint requires a JWT.

**Worker** — confirm it started:

```bash
docker compose logs worker --tail 5
```

You should see `worker started`. The worker prints a line every time it picks up a job.

### Frontend (React app)

Open http://localhost:5173 in your browser. You should see "Token Trail" and a green health-check JSON block from the backend. If it shows an error, the backend probably isn't reachable — check that `token-trail-backend` is running.

**Submission comparison view:** From Dashboard, go to a course (e.g. COSC 4P02) → Assignment 1, then click "View submission comparison". Or navigate directly to `/course/1/assignment/a1/submission/dummy-submission-id`. The page shows student details, similarity metrics, side-by-side code panels, and a list of similarity candidates (all dummy data for now).

### Both (Docker + shared env)

Quick one-liner to see all container statuses:

```bash
docker compose ps
```

All four services should show `Up` (or `running`).

---

## 3) Full End-to-End Happy Path (Do This Once)

Walk through this after your first `docker compose up --build`. Use Swagger UI at http://localhost:8000/docs — it's the easiest way.

### Step 1 — Sign up an instructor

**`POST /api/auth/signup`**

```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "password": "secret123"
}
```

Expected `201`:

```json
{ "accessToken": "eyJhbGciOi..." }
```

Copy the `accessToken` value.

### Step 2 — Authorize in Swagger

1. Click the **Authorize** button (lock icon, top-right of Swagger UI).
2. In the **Value** field, paste the token you copied (just the token string, no "Bearer" prefix — Swagger adds it).
3. Click **Authorize**, then **Close**.

All locked endpoints will now use your token.

### Step 3 — Create a course

**`POST /api/instructor/courses`**

```json
{
  "name": "CS101",
  "term": "Fall 2025"
}
```

Expected `201`:

```json
{
  "id": "665f...",
  "name": "CS101",
  "term": "Fall 2025",
  "instructorId": "665e...",
  "createdAt": "2025-..."
}
```

Copy the `id` — that's your `courseId`.

### Step 4 — Create an assignment

**`POST /api/instructor/assignments`**

```json
{
  "courseId": "<courseId from step 3>",
  "title": "HW1 Sorting",
  "language": "java",
  "isOpen": true,
  "dueDate": "2025-06-08T23:59:59+00:00",
  "keyExpiry": "2025-06-09T00:00:00+00:00",
  "autoAnalysis": false,
  "allowLate": false,
  "exclusionCode": null
}
```

Expected `201`:

```json
{
  "id": "665f...",
  "courseId": "665f...",
  "title": "HW1 Sorting",
  "language": "java",
  "assignmentKey": "4829103756",
  "isOpen": true,
  "dueDate": "2025-06-08T23:59:59+00:00",
  "keyExpiry": "2025-06-09T00:00:00+00:00",
  "autoAnalysis": false,
  "allowLate": false,
  "exclusionCode": null,
  "createdAt": "2025-..."
}
```

Copy both `id` (= assignmentId) and `assignmentKey`.

### Step 5 — Validate the assignment key (public)

**`POST /api/public/assignment-key/validate`** *(no auth needed)*

```json
{
  "assignmentKey": "<key from step 4>"
}
```

Expected `200`:

```json
{
  "valid": true,
  "assignment": { "id": "665f...", "language": "java", "isOpen": true }
}
```

### Step 6 — Upload a student ZIP submission (public)

**`POST /api/public/submissions`** *(multipart/form-data, no auth needed)*

| Field | Value |
|-------|-------|
| `assignmentKey` | the 10-digit key from step 4 |
| `studentIdentifier` | `student1@uni.edu` |
| `studentName` | `Test Student` |
| `zipFile` | a `.zip` containing at least one `.java` file |

> **Tip:** Create a quick test zip — put a `Hello.java` in a folder and zip it.

Expected `201`:

```json
{
  "submissionId": "665f...",
  "status": "processed",
  "fileCount": 1,
  "mergedCreated": true
}
```

Behind the scenes the backend:
1. Saved the raw zip to `uploads/<assignmentId>/<submissionId>/raw.zip`
2. Safe-extracted it (blocking `../` traversal and absolute paths)
3. Filtered for valid `.java` files
4. Merged them into `uploads/<assignmentId>/<submissionId>/merged/merged.txt`
5. Stored a Submission document in MongoDB

### Step 7 — View submissions as the instructor

**`GET /api/instructor/assignments/<assignmentId>/submissions`**

Expected `200`:

```json
[
  {
    "submissionId": "665f...",
    "assignmentId": "665f...",
    "studentIdentifier": "student1@uni.edu",
    "studentName": "Test Student",
    "submittedAt": "2025-...",
    "fileCount": 1,
    "status": "processed"
  }
]
```

### Step 8 — Queue an analysis run

**`POST /api/instructor/assignments/<assignmentId>/analysis-runs`**

*(No request body needed.)*

Expected `201`:

```json
{ "runId": "665f...", "status": "queued", "algorithmVersion": "v0" }
```

Copy the `runId`.

### Step 9 — Watch the worker process it

**`GET /api/instructor/analysis-runs/<runId>`**

Expected `200` (after a few seconds):

```json
{
  "runId": "665f...",
  "assignmentId": "665f...",
  "status": "completed",
  "algorithmVersion": "v0",
  "createdAt": "...",
  "startedAt": "...",
  "finishedAt": "...",
  "errorMessage": null
}
```

The worker polls MongoDB every 5 seconds. It atomically claims one `queued` job, sets it to `running`, calls the analysis stub, then marks it `completed` (or `failed` with an `errorMessage`).

Right now the analysis engine is a stub (no-op), so the run completes instantly. The real tokenisation + winnowing pipeline will be added later.

### Common failure responses (expected)

Use these to quickly confirm contract behavior during final confidence checks:

- `POST /api/auth/signup` (duplicate email) -> `409` with `{"detail":"Email already registered"}`
- `GET /api/auth/me` (no token) -> `401` with `{"detail":"Not authenticated"}`
- `GET /api/instructor/assignments/not-an-id` -> `400` with `{"detail":"Invalid ID format: not-an-id"}`
- `POST /api/public/assignment-key/validate` (unknown key) -> `200` with `{"valid":false,"assignment":null}`
- `GET /api/instructor/analysis-runs/{runId}` as a different instructor -> `403` with `{"detail":"Not your analysis run"}`

---

## 4) Repo Structure (What Lives Where)

### Backend (API + Worker + Mongo)

```
backend/
├── requirements.txt                   Python dependencies (FastAPI, pymongo, bcrypt, etc.)
└── app/
    ├── main.py                        FastAPI app, CORS, /api/health, router registration
    ├── core/
    │   ├── config.py                  Reads env vars (Mongo, JWT, uploads, retention/privacy placeholders, etc.)
    │   ├── db.py                      PyMongo client singleton and get_db() helper
    │   ├── security.py                bcrypt password hashing + JWT create/verify (HS256)
    │   └── deps.py                    get_current_instructor() auth guard + to_object_id()
    ├── middleware/
    │   └── rate_limit.py              Stub — future rate-limit enforcement helpers
    ├── routers/
    │   ├── auth.py                    POST /signup, POST /login, GET /me
    │   ├── public.py                  POST /assignment-key/validate, POST /submissions
    │   ├── instructor.py              Courses, assignments, submissions list, analysis runs
    │   ├── instructor_similarity.py   Stub routes for ranked results, pair detail, side-by-side compare
    │   └── instructor_admin.py        Stub routes for key mgmt/admin actions (returns 501)
    ├── schemas/                       Pydantic models defining request/response shapes
    │   ├── auth.py                    SignupRequest, LoginRequest, AuthResponse, MeResponse
    │   ├── course.py                  CourseCreateRequest, CourseResponse
    │   ├── assignment.py              AssignmentCreate/Update/Response (+ dueDate/keyExpiry/autoAnalysis/allowLate/exclusionCode)
    │   ├── public.py                  ValidateKeyRequest/Response, SubmissionResponse
    │   ├── analysis.py                CreateRunResponse, RunStatusResponse
    │   ├── similarity.py              Stub response shapes for similarity-report flow
    │   ├── exclusion.py               Stub request/response shapes for exclusion-code CRUD
    │   └── class_list.py              Stub request/response shapes for class-list management
    ├── services/
    │   ├── zip_service.py             safe_extract_zip, list_valid_source_files, is_binary_file
    │   ├── merge_service.py           merge_source_files (deterministic, sorted, with headers)
    │   ├── submission_service.py      create_submission helper (inserts Mongo doc)
    │   ├── analysis_service.py        Stub (no-op) — will hold the winnowing pipeline
    │   ├── retention_service.py       Stub — future 30-day cleanup/purge flow
    │   ├── anonymization_service.py   Stub — future student pseudonymization/hashing flow
    │   └── notification_service.py    Stub — future submission confirmation/replacement emails
    ├── models/                        Reserved for future data-model helpers
    ├── analysis/                      Reserved for tokenisation + winnowing engine code
    └── worker/
        └── worker.py                  Standalone polling loop: claims queued runs, executes them
```

### Frontend (React app)

```
frontend/
├── package.json                       Dependencies (React 18, Vite 5)
├── vite.config.js                     Vite config (host 0.0.0.0 for Docker)
├── index.html                         HTML shell
├── .env.example                       VITE_API_BASE_URL default
├── docker-entrypoint.sh               Runs npm install (if needed) + npm run dev in Docker
└── src/
    ├── main.jsx                       React root
    ├── App.jsx                        Routes, health check, instructor layout
    ├── routes.jsx                     Skeleton route placeholders for future router wiring
    ├── index.css                      Base styles, Tailwind theme
    ├── constants/
    │   └── submissionComparison.js    Dummy data for submission comparison view
    ├── components/
    │   ├── Sidebar/                   Sidebar nav (courses, assignments)
    │   ├── SubmissionComparison/      Submission comparison UI components
    │   │   ├── MetricsCard.jsx        Metric display (value + label, color)
    │   │   ├── CodeComparisonPanel.jsx File dropdown, code display
    │   │   └── SimilarityCandidatesList.jsx Clickable similarity candidate list
    │   ├── SimilarityRankedList.jsx   Stub — ranked similarity rows
    │   └── CodeComparison.jsx         Stub — side-by-side highlighted compare
    ├── services/
    │   └── api.js                     apiFetch(), getInstructorAssignmentById, getAssignmentSubmissions,
    │                                  queueAnalysisRun, getAnalysisRunStatus, getSimilarityResults,
    │                                  getSimilarityComparison (stubs for 501 endpoints)
    └── pages/
        ├── LoginPage.jsx              Stub — wire up to POST /api/auth/login
        ├── StudentSubmitPage.jsx      Stub — wire up to POST /api/public/submissions
        ├── InstructorDashboardPage.jsx Stub — wire up to GET /api/instructor/courses
        ├── CoursePage.jsx             Course page with sidebar
        ├── AssignmentPage.jsx         Assignment page; link to submission comparison
        ├── SubmissionComparisonPage.jsx Implemented — submission detail + side-by-side comparison (dummy data)
        ├── AssignmentDetailPage.jsx   Load by ID, submissions table, analysis run controls (not routed)
        ├── SimilarityReportPage.jsx   Stub — ranked results list page
        ├── SimilarityPairDetailPage.jsx Stub — pair drill-down page
        └── SimilarityComparisonPage.jsx Stub — side-by-side highlighted comparison page
```

### Both (Docker + shared env)

```
docker/
├── Dockerfile.backend                 Python 3.12-slim, installs requirements, runs uvicorn
├── Dockerfile.worker                  Same image, runs python -m app.worker.worker
└── Dockerfile.frontend                Node 20-alpine, npm install, Vite dev server

docker-compose.yml                     Defines all 4 services, volumes, ports, env
.env.example                           Template for environment variables
.gitignore                             Ignores .env, uploads/*, node_modules, __pycache__, etc.
uploads/                               Student ZIP + extracted + merged files (git-ignored)
└── .gitkeep                           Tracked so the folder exists on clone
docs/
├── TEAM_SETUP.md                      This file
├── SETUP.md                           Shorter quick-start + troubleshooting
├── API_CONTRACT.md                    Full endpoint reference with request/response examples
└── CONTRIBUTING.md                    Branching, PR, and code-style rules
.github/
├── pull_request_template.md           PR checklist (auto-loaded when you open a PR)
└── ISSUE_TEMPLATE/
    ├── bug_report.md                  Bug report template
    └── feature_request.md             Feature request template
```

---

## 5) Development Workflow (What To Do When You Change Things)

### Backend (API + Worker + Mongo)

| What you changed | What to do |
|------------------|-----------|
| Any `.py` file in `backend/` | The container sees it immediately via the bind mount (`./backend:/app`). **Restart the backend container** to pick up the change: `docker compose restart backend`. If you add `--reload` to the uvicorn command in `docker-compose.yml`, changes apply automatically without restarting. |
| `backend/requirements.txt` | **Rebuild the image:** `docker compose up --build backend`. Same for the worker: `docker compose up --build worker`. |
| Worker code (`worker.py`, services) | Restart the worker: `docker compose restart worker`. |

**View logs:**

```bash
docker compose logs -f backend        # API logs
docker compose logs -f worker         # Worker logs (watch for "claimed run ...")
docker compose logs -f mongodb        # Mongo logs (rarely needed)
```

### Frontend (React app)

| What you changed | What to do |
|------------------|-----------|
| Any `.jsx`, `.js`, or `.css` file in `frontend/src/` | Vite hot-module replacement picks it up instantly. Just save and check the browser. |
| `frontend/package.json` (added a dependency) | **Rebuild the image:** `docker compose up --build frontend`. Or, if running outside Docker: `cd frontend && npm install`. |

**View logs:**

```bash
docker compose logs -f frontend
```

### Both (Docker + shared env)

| What you changed | What to do |
|------------------|-----------|
| `docker-compose.yml` | Stop and restart: `docker compose down && docker compose up --build` |
| `.env` | Restart the affected service(s): `docker compose restart backend worker` |

**Reset everything (nuclear option):**

```bash
docker compose down -v
```

> **Warning:** the `-v` flag deletes the `mongodb_data` volume, which **erases all Mongo data**. Use it only when you want a completely fresh database.

Then start fresh:

```bash
docker compose up --build
```

---

## 6) API Contract Summary (Stable Shapes)

Full details with every field are in **[docs/API_CONTRACT.md](API_CONTRACT.md)**. Here's a quick cheat-sheet.

**Fixed prefixes** — do not change these:

| Prefix | Auth | Who uses it |
|--------|------|-------------|
| `/api/health` | none | Everyone (smoke test) |
| `/api/auth` | none (signup/login) or Bearer (me) | Instructors |
| `/api/public` | none (key-gated) | Students |
| `/api/instructor` | Bearer JWT | Instructors |

**Key response shapes:**

```
POST /api/auth/signup       → { "accessToken": "..." }
POST /api/auth/login        → { "accessToken": "..." }
GET  /api/auth/me           → { "id", "name", "email" }

POST /api/public/assignment-key/validate
  → { "valid": true, "assignment": { "id", "language", "isOpen" } }

POST /api/public/submissions (multipart)
  → { "submissionId", "status", "fileCount", "mergedCreated" }

POST /api/instructor/assignments/{id}/analysis-runs
  → { "runId", "status": "queued", "algorithmVersion": "v0" }

GET  /api/instructor/analysis-runs/{runId}
  → { "runId", "assignmentId", "status", "algorithmVersion",
      "createdAt", "startedAt", "finishedAt", "errorMessage" }

GET  /api/instructor/analysis-runs/{runId}/similarity-results
GET  /api/instructor/similarity-results/{resultId}
GET  /api/instructor/similarity-results/{resultId}/comparison
  → currently placeholder routes returning 501 (skeleton contract only)

POST /api/instructor/assignments/{id}/regenerate-key
POST /api/instructor/assignments/{id}/expire-key
GET  /api/instructor/assignments/{id}/submissions/download
DELETE /api/instructor/assignments/{id}/submissions
DELETE /api/instructor/assignments/{id}
GET/PUT/DELETE /api/instructor/assignments/{id}/exclusion-code
GET/PUT/POST /api/instructor/courses/{id}/class-list
  → currently placeholder routes returning 501 (skeleton contract only)
```

**Enums (use these exact strings):**

| Model | Field | Values |
|-------|-------|--------|
| `AnalysisRun` | `status` | `queued`, `running`, `completed`, `failed` |
| `Submission` | `status` | `queued`, `processed`, `failed` |

**ZIP submission merge pipeline:**

When a student uploads a ZIP via `POST /api/public/submissions`, the backend runs this pipeline synchronously before returning a response:

1. **Safe-extract** the ZIP — any entry containing `../` or starting with `/` or `\` is silently skipped (prevents path traversal attacks).
2. **Filter** by assignment language:
   - `java` → `.java`
   - `c` → `.c`, `.h`
   - `cpp` → `.cpp`, `.hpp`, `.h`
   - Binary files (null bytes in first 8 KB) are also skipped.
3. **Sort** valid files by relative POSIX path (alphabetical, deterministic).
4. **Merge** into a single text file. Each file section starts with a header line:
   ```
   //// FILE: path/to/File.java
   ```
5. **Output** is written to:
   ```
   uploads/<assignmentId>/<submissionId>/merged/merged.txt
   ```

This merged file is the input the analysis engine will later read when computing fingerprints and similarity scores.

**Architecture notes:**

- **No Redis / no Celery.** The worker is a simple Python loop that polls the `analysis_runs` MongoDB collection every 5 seconds. It uses `find_one_and_update` to atomically claim one `queued` job, which prevents two workers from processing the same run.
- **JWT auth** uses HS256 via `python-jose`. Tokens expire after `JWT_EXPIRES_MINUTES` (default 60). The `get_current_instructor` dependency in `core/deps.py` validates the token and loads the instructor from MongoDB.
- **Uploads persist** via the Docker Compose volume mount `./uploads:/app/uploads`. Files survive container restarts. They are git-ignored (only `uploads/.gitkeep` is tracked).
- **SRS placeholders** for admin actions, key management, similarity-report APIs, retention/privacy, notifications, and rate-limits are intentionally scaffold-only right now. New placeholder endpoints return HTTP `501`.

---

## 7) Team Collaboration Rules

Full rules are in **[docs/CONTRIBUTING.md](CONTRIBUTING.md)**. Quick summary:

### Branching

- **Never push directly to `main`.**
- Name your branches:
  - `feature/<short-name>` — e.g. `feature/winnowing-engine`
  - `fix/<short-name>` — e.g. `fix/zip-empty-file`

### Pull Requests

- Keep PRs small — aim for **≤ 300 changed lines**.
- Write a short description of *what* and *why*.
- Link related issues (e.g. `Fixes #12`).
- At least **1 approval** required before merge.
- Squash-merge into `main`.
- Use the PR template (`.github/pull_request_template.md`) — it loads automatically when you open a PR on GitHub.

### Issues

Use the templates in `.github/ISSUE_TEMPLATE/`:

- **Bug report** — describe what happened, steps to reproduce, expected behaviour.
- **Feature request** — describe the feature, use case, and (optionally) proposed solution.

### Code style

- **Python:** PEP 8, type hints where practical.
- **JavaScript / React:** functional components.
- Add short comments for non-obvious logic.
- **Never commit `.env` files or secrets.** If you don't have the required `.env` values, ask the repo owner — we only commit `.env.example` to keep secrets out of Git.

### Commit messages

Use present-tense imperative mood:

- "Add signup endpoint"
- "Fix ZIP path traversal check"
- "Update SETUP.md with Docker troubleshooting"
