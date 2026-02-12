# Token-Trail

Token Trail is a web-based, instructor-facing code similarity detection system designed to help academic staff review programming assignment submissions for suspicious similarity. Instructors create courses and assignments, generate a unique **10-digit assignment key**, optionally upload **exclusion (boilerplate) code**, ingest student **ZIP submissions** (no student accounts), and trigger analysis runs that tokenize/normalize code, generate **winnowing-based fingerprints**, compute similarity scores, and display ranked results with a side-by-side comparison view highlighting matching regions.

## Constraints (per SRS / course rules)
- ✅ We build our own analysis engine (no MOSS or plagiarism APIs)
- ✅ Supported languages: **Java, C, C++**
- ✅ Homogeneous repos per assignment (one language per assignment set)
- ✅ Students submit via assignment key only (no student accounts)

---

## Key Features

**Student (Public)**
- Validate a 10-digit assignment key
- Upload assignment as a ZIP submission
- Receive a submission confirmation

**Instructor (Authenticated)**
- Sign up / log in
- Create courses and assignments
- Generate assignment keys
- Upload exclusion (boilerplate) code
- View submissions and trigger analysis runs
- View ranked similarity reports
- Compare files side-by-side with highlighted matching regions

---

## Tech Stack

**Frontend**
- React + Vite
- PrismJS for syntax highlighting in the compare view

**Backend API**
- FastAPI (Python)
- Handles auth, course/assignment management, student submissions (ZIP upload), and analysis-run orchestration

**Analysis Engine (Worker)**
- Python worker process (separate from API)
- Runs tokenization → normalization → winnowing → similarity scoring
- Writes `SimilarityResult` records

**Database**
- MongoDB
- Stores entities from the data dictionary (Instructor, Course, Assignment, Submission, AnalysisRun, SimilarityResult, etc.)

**File Storage**
- Local disk folder in dev (`/uploads`) for ZIPs + extracted files  
  *(Later can be S3/MinIO, not needed early.)*

**Auth**
- JWT (JSON Web Tokens)
- Instructor-only protected routes; student upload routes are public (key-gated)

---

## Monorepo Structure

```txt
token-trail/
  frontend/         # React UI (student upload + instructor portal)
  backend/          # FastAPI server + analysis engine + worker
  docs/             # SRS, diagrams, and API notes
  docker/           # Dockerfiles
  docker-compose.yml
  .env.example
