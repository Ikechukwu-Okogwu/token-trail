# Token Trail — Demo Runbook
> Verified against live stack 2026-03-18. Full e2e flow: 26/26 tests pass.

---

## Pre-Demo Checklist (do 10 min before)

```bash
cd token-trail
docker compose ps          # all 4 containers must show "Up"
curl http://localhost:8000/api/health   # expect {"status":"ok"}
```

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | Frontend (show to audience) |
| http://localhost:8000/docs | Swagger fallback |
| http://localhost:8000/api/health | Backend health badge |

**Test ZIPs** — already in repo:
```
backend/app/analysis/localtest/submission_files/
  original.zip   ← Alice's real submission
  copied.zip     ← Bob's plagiarised copy  (93.5% similar to original)
  changed.zip    ← Carol's modified version (43% similar)
```
For regression fixture ZIP sets and expected-score contracts, see `docs/TEST_ZIPS.md`.

**Demo account** — sign up fresh each time or reuse:
- Email: `demo@tokentrail.test`
- Password: `DemoPass2026!`

**Assignment language must be** `java`, `c`, or `cpp`.

---

## 1. UI Demo Script (~5–7 min)

### [0:00] Landing Page
> "Token Trail detects code plagiarism in student submissions. There are two entry points."

- Open **http://localhost:5173**
- Point to the two cards: **Student** and **Teacher**

---

### [0:30] Instructor Login
> "The instructor logs in here. Login saves a JWT token — all dashboard calls are authenticated."

- Click **Teacher**
- Sign Up (or Sign In) with `demo@tokentrail.test` / `DemoPass2026!`
- You land on **/dashboard**
- Point to the API health badge bottom-right: `API: ok`

---

### [1:00] Dashboard — Real Courses
> "The sidebar and dashboard both fetch live data from the backend. No fake data."

- Show the course list (real API, `GET /instructor/courses`)
- Click **+ New** → create course: name `COSC 4P02`, term `Winter 2026`
- Course card appears immediately

---

### [1:45] Course Page — Create Assignment
> "Each course holds assignments. We create one now."

- Click the course card → **Course Page**
- Click **+ New** → fill in:
  - Title: `Assignment 1 - Sorting Algorithms`
  - Language: `Java`
  - Open: checked
- Assignment card appears. Note the **Assignment Key** shown.

---

### [2:30] Student Submit Flow
> "Students submit without an account — they just need the key."

- Open a **new tab** → http://localhost:5173/student-submit
- Enter the assignment key
- Upload `original.zip` as `alice@demo.test` (Alice Smith)
- Upload `copied.zip` as `bob@demo.test` (Bob Jones)
- Upload `changed.zip` as `carol@demo.test` (Carol Lee)
- Each shows a success confirmation

> "Three students submitted. Alice's is the original. Bob copied it almost verbatim. Carol made modifications."

---

### [3:30] Assignment Detail — Queue Analysis
> "Back on the instructor side — we can see all three submissions came in."

- Switch back to instructor tab → click the assignment
- **Assignment Detail Page**: submissions table shows Alice, Bob, Carol — all `processed`
- Click **Run Analysis**
- Status badge flips: `QUEUED` → `RUNNING` → `COMPLETED`

> "The worker picked it up immediately. In production this would run async."

---

### [4:15] Similarity Results
> "Now the system tells us who copied whom."

- Click the green **View Similarity Results** button
- **Similarity Report Page** loads — 3 pairs ranked by score:
  - **93.5%** — Alice ↔ Bob (red) ← this is the catch
  - 43.9% — Bob ↔ Carol
  - 43.4% — Alice ↔ Carol
- Point to the red row: "93.5% is a near-identical copy."
- Click **View →** on the top row

---

### [4:45] Pair Detail
> "We can drill into any pair and see the metadata."

- **Pair Detail Page**: score, both submission IDs, summary
- Click **Open Comparison →**

---

### [5:00] Side-by-Side Comparison
> "Here is the code, side-by-side. Alice's original on the left, Bob's copy on the right. The similarity score is shown in the header."

- **Comparison Page**: two dark code panes with line numbers
- Scroll through both — they are nearly identical
- Score banner shows `93.5% similar`

> "This is the evidence an instructor would use to flag the case."

---

## 2. Backup: Swagger Demo (if frontend fails)

Open **http://localhost:8000/docs**

Run in this order using **Try it out**:

| # | Endpoint | Key inputs |
|---|----------|-----------|
| 1 | `POST /api/auth/signup` | `name`, `email`, `password` |
| 2 | Click **Authorize** (top right) → paste `accessToken` | |
| 3 | `POST /api/instructor/courses` | `name`, `term` |
| 4 | `POST /api/instructor/assignments` | `courseId`, `title`, `language: java`, `isOpen: true` |
| 5 | `POST /api/public/assignment-key/validate` | `assignmentKey` from step 4 |
| 6 | `POST /api/public/submissions` (×3) | `assignmentKey`, `studentIdentifier`, `zipFile` |
| 7 | `GET /api/instructor/assignments/{id}/submissions` | confirm 3 rows |
| 8 | `POST /api/instructor/assignments/{id}/analysis-runs` | save `runId` |
| 9 | `GET /api/instructor/analysis-runs/{runId}` | repeat until `completed` |
| 10 | `GET /api/instructor/analysis-runs/{runId}/similarity-results` | show ranked pairs |
| 11 | `GET /api/instructor/similarity-results/{resultId}` | top pair metadata |
| 12 | `GET /api/instructor/similarity-results/{resultId}/comparison` | `leftCode` / `rightCode` side-by-side |

---

## 3. The Story the Data Tells

| Student | ZIP | Score vs Alice | Interpretation |
|---------|-----|---------------|----------------|
| Alice Smith | `original.zip` | baseline | Legitimate submission |
| Bob Jones | `copied.zip` | **93.5%** | Near-verbatim copy — flagged |
| Carol Lee | `changed.zip` | 43.4% | Modified version — borderline |

The system surfaces Bob's copy automatically. No manual diff required.

---

## 4. Known Caveats (if asked)

| Caveat | What to say |
|--------|------------|
| **No line highlights** in comparison view | `matchingRegions` is `[]` in the baseline engine. Side-by-side code is shown; inline highlighting is a next iteration. |
| **RUNNING state may be instant** | The worker is fast on the demo dataset. In production with larger submissions, you'd watch it transition through QUEUED → RUNNING → COMPLETED. |
| **Assignment language limited** | Backend accepts `java`, `c`, `cpp` only. The form already restricts to these options. |

---

## 5. Emergency Reset

If data looks wrong, wipe and restart:

```bash
docker compose down -v
docker compose up -d
# Wait ~10s for MongoDB healthy, then re-run the demo from Login.
```
