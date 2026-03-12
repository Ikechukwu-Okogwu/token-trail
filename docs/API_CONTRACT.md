# Token Trail — API Contract

**Base URL:** `http://localhost:8000`
**Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
**ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

All request/response bodies are JSON unless otherwise noted.
Protected routes require `Authorization: Bearer <token>`.

> Skeleton note: some endpoints are contract placeholders only and intentionally return `501 Not Implemented` with:
> `{ "status": "not_implemented", "feature": "<feature_key>", "message": "Skeleton placeholder endpoint. Implementation planned in future sprint." }`

---

## Health Check

### `GET /api/health`

Response `200`:
```json
{ "status": "ok", "service": "token-trail-api" }
```

---

## Auth

### `POST /api/auth/signup`

Request:
```json
{ "name": "Alice", "email": "alice@example.com", "password": "secret123" }
```

Response `201`:
```json
{ "accessToken": "eyJhbGciOi..." }
```

Errors: `409` email already registered.

---

### `POST /api/auth/login`

Request:
```json
{ "email": "alice@example.com", "password": "secret123" }
```

Response `200`:
```json
{ "accessToken": "eyJhbGciOi..." }
```

Errors: `401` invalid email or password.

---

### `GET /api/auth/me`

Headers: `Authorization: Bearer <token>`

Response `200`:
```json
{ "id": "665f...", "name": "Alice", "email": "alice@example.com" }
```

Errors: `401` invalid / missing token.

---

## Instructor (JWT required)

### `POST /api/instructor/courses`

Request:
```json
{ "name": "CS101", "term": "Fall 2025" }
```

Response `201`:
```json
{
  "id": "665f...",
  "name": "CS101",
  "term": "Fall 2025",
  "instructorId": "665e...",
  "createdAt": "2025-06-01T12:00:00+00:00"
}
```

---

### `GET /api/instructor/courses`

Response `200`: array of `CourseResponse`.

---

### `POST /api/instructor/assignments`

Request:
```json
{
  "courseId": "665f...",
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

Response `201`:
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
  "createdAt": "2025-06-01T12:00:00+00:00"
}
```

---

### `PATCH /api/instructor/assignments/{assignmentId}`

Request (all fields optional):
```json
{
  "isOpen": false,
  "dueDate": "2025-06-08T23:59:59+00:00",
  "keyExpiry": "2025-06-09T00:00:00+00:00",
  "autoAnalysis": true,
  "allowLate": true,
  "exclusionCode": "starter template"
}
```

Response `200`: full `AssignmentResponse`.

---

### `GET /api/instructor/assignments/{assignmentId}`

Response `200`: `AssignmentResponse`.

---

### `GET /api/instructor/assignments/{assignmentId}/submissions`

Response `200`:
```json
[
  {
    "submissionId": "665f...",
    "assignmentId": "665f...",
    "studentIdentifier": "alice@uni.edu",
    "studentName": "Alice",
    "submittedAt": "2025-06-02T09:30:00+00:00",
    "fileCount": 5,
    "status": "processed"
  }
]
```

---

### `POST /api/instructor/assignments/{assignmentId}/analysis-runs`

Response `201`:
```json
{ "runId": "665f...", "status": "queued", "algorithmVersion": "v0" }
```

---

### `GET /api/instructor/analysis-runs/{runId}`

Response `200`:
```json
{
  "runId": "665f...",
  "assignmentId": "665f...",
  "status": "completed",
  "algorithmVersion": "v0",
  "createdAt": "2025-06-02T10:00:00+00:00",
  "startedAt": "2025-06-02T10:00:01+00:00",
  "finishedAt": "2025-06-02T10:00:05+00:00",
  "errorMessage": null
}
```

`status` enum: `queued` | `running` | `completed` | `failed`.

Errors:
- `401` invalid / missing token
- `403` analysis run belongs to another instructor
- `404` run or backing assignment not found

---

## Public (no JWT)

### `POST /api/public/assignment-key/validate`

Request:
```json
{ "assignmentKey": "4829103756" }
```

Response `200`:
```json
{
  "valid": true,
  "assignment": { "id": "665f...", "language": "java", "isOpen": true }
}
```

If key is not found:
```json
{ "valid": false, "assignment": null }
```

---

### `POST /api/public/submissions`

Content-Type: `multipart/form-data`

| Field               | Type   | Required |
|---------------------|--------|----------|
| `assignmentKey`     | string | yes      |
| `studentIdentifier` | string | yes      |
| `studentName`       | string | no       |
| `zipFile`           | file   | yes      |

Response `201`:
```json
{
  "submissionId": "665f...",
  "status": "processed",
  "fileCount": 7,
  "mergedCreated": true
}
```

**Submission pipeline:**
1. Validate assignment key.
2. Save raw ZIP to `uploads/<assignmentId>/<submissionId>/raw.zip`.
3. Safe-extract (path traversal blocked).
4. Filter valid source files by assignment language.
5. Merge files deterministically (sorted by relative path, with `//// FILE:` headers).
6. Store Submission document (`status: "processed"`).

---

## Running Outside Docker

When running the backend directly on your machine instead of in Docker, set:

```
MONGO_URI=mongodb://localhost:27017
```

---

## Instructor Placeholder Endpoints (`501`)

All endpoints below are deliberate skeleton contracts and currently return `501 Not Implemented`.

### Similarity Report Flow

- `GET /api/instructor/analysis-runs/{runId}/similarity-results`
- `GET /api/instructor/similarity-results/{resultId}`
- `GET /api/instructor/similarity-results/{resultId}/comparison`

**Frontend status:** The submission comparison UI is implemented (`SubmissionComparisonPage`, route `/course/:courseId/assignment/:assignmentId/submission/:submissionId`). It uses dummy data and API client stubs (`getSimilarityResults`, `getSimilarityComparison` in `frontend/src/services/api.js`). When the backend implements these endpoints, the frontend expects the response shapes documented in the JSDoc comments in `api.js` (per SRS 4.3.2 Ranked Similarity Results and 4.3.3 Detailed Comparison Report).

### Assignment Key Management

- `POST /api/instructor/assignments/{assignmentId}/regenerate-key`
- `POST /api/instructor/assignments/{assignmentId}/expire-key`

### Instructor Admin Actions

- `GET /api/instructor/assignments/{assignmentId}/submissions/download`
- `DELETE /api/instructor/assignments/{assignmentId}/submissions`
- `DELETE /api/instructor/assignments/{assignmentId}`
- `GET /api/instructor/assignments/{assignmentId}/exclusion-code`
- `PUT /api/instructor/assignments/{assignmentId}/exclusion-code`
- `DELETE /api/instructor/assignments/{assignmentId}/exclusion-code`
- `GET /api/instructor/courses/{courseId}/class-list`
- `PUT /api/instructor/courses/{courseId}/class-list`
- `POST /api/instructor/courses/{courseId}/class-list`
