## What does this PR do?
<!-- Briefly explain WHAT changed + WHY (1–5 bullets). -->
- 

## Related Issues
<!-- Link issues if you’re using GitHub Issues. -->
<!-- Examples: Closes #12, Fixes #34 -->
- N/A (no issue created)

## How to test
<!-- Write the exact steps you ran. If docs-only, say “N/A (docs only)”. -->

### Both (Docker)
- [ ] `Copy-Item .env.example .env` (Windows) / `cp .env.example .env` (Mac/Linux)
- [ ] `docker compose up --build`

### Backend (API)
- [ ] Open `http://localhost:8000/api/health` → should return `{ "status": "ok", ... }`
- [ ] Open `http://localhost:8000/docs` → Swagger loads

### Frontend (React)
- [ ] Open `http://localhost:5173` → page loads + health JSON shows

### End-to-end happy path (only if relevant)
- [ ] `POST /api/auth/signup` → get token
- [ ] Authorize in Swagger (Bearer token)
- [ ] `POST /api/instructor/courses`
- [ ] `POST /api/instructor/assignments` → get `assignmentKey`
- [ ] `POST /api/public/assignment-key/validate`
- [ ] `POST /api/public/submissions` (multipart zip upload)
- [ ] Confirm merged output exists:
  - `uploads/<assignmentId>/<submissionId>/merged/merged.txt`
- [ ] `POST /api/instructor/assignments/{id}/analysis-runs`
- [ ] `GET /api/instructor/analysis-runs/{runId}` → status moves `queued → running → completed/failed`

## Checklist
- [ ] PR is small & focused (not a mega-PR)
- [ ] Swagger contract still correct (`/docs`)
- [ ] No secrets committed (no `.env`)
- [ ] If dependencies changed, images were rebuilt (`docker compose up --build`)