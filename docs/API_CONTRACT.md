# Token Trail — API Contract

**Base URL:** `http://localhost:8000`
**Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
**ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

All request/response bodies are JSON unless otherwise noted.
Protected routes require `Authorization: Bearer <token>`.

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

Errors:
- `409` email already registered

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

Errors:
- `401` invalid credentials
- `429` rate-limited (if enabled)

---

### `GET /api/auth/me`

Response `200`:
```json
{ "id": "665f...", "name": "Alice", "email": "alice@example.com" }
```

Errors:
- `401` invalid / missing token

---

## Instructor (JWT required)

### `POST /api/instructor/courses`

Response `201`: `CourseResponse`

---

### `GET /api/instructor/courses`

Response `200`: array of `CourseResponse`

---

### `GET /api/instructor/courses/{courseId}/assignments`

Response `200`: array of `AssignmentResponse`

Errors:
- `400` invalid course ID format
- `404` course not found

---

### `POST /api/instructor/assignments`

Creates assignment with unique 10-digit `assignmentKey`.

Response `201`: `AssignmentResponse`

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

Response `200`: full `AssignmentResponse`

---

### `GET /api/instructor/assignments/{assignmentId}`

Response `200`: `AssignmentResponse`

---

### `GET /api/instructor/assignments/{assignmentId}/submissions`

Response `200`: array of `SubmissionListItem`

---

### `POST /api/instructor/assignments/{assignmentId}/analysis-runs`

Response `201`:
```json
{ "runId": "665f...", "status": "queued", "algorithmVersion": "v0" }
```

---

### `GET /api/instructor/analysis-runs/{runId}`

Response `200`: run status payload  
`status` enum: `queued` | `running` | `completed` | `failed`

---

### `GET /api/instructor/analysis-runs/{runId}/similarity-results`

Response `200`: ranked similarity pairs payload

---

### `GET /api/instructor/similarity-results/{resultId}`

Response `200`: pair detail payload

---

### `GET /api/instructor/similarity-results/{resultId}/comparison`

Response `200`: comparison payload (`leftCode`, `rightCode`, `matchingRegions`, etc.)

---

## Instructor Admin (JWT + assignment ownership)

### `POST /api/instructor/assignments/{assignmentId}/regenerate-key`

Regenerates assignment key and invalidates previous key.

Response `200`: `AssignmentResponse` (with new `assignmentKey`)

---

### `POST /api/instructor/assignments/{assignmentId}/expire-key`

Expires assignment key immediately by setting `keyExpiry` to current UTC time.

Response `200`: `AssignmentResponse`

---

### `GET /api/instructor/assignments/{assignmentId}/submissions/download`

Downloads all submissions as a ZIP.

Response `200` with headers:
- `Content-Type: application/zip`
- `Content-Disposition: attachment; filename="assignment-<assignmentId>-submissions.zip"`

Archive currently includes available:
- `<submissionId>/raw.zip`
- `<submissionId>/merged/merged.txt`

---

### `DELETE /api/instructor/assignments/{assignmentId}/submissions`

Deletes assignment submissions from MongoDB and disk (`UPLOAD_DIR/<assignmentId>`).

Response `204` (idempotent)

---

### `DELETE /api/instructor/assignments/{assignmentId}`

Deletes assignment and cascades related submissions, analysis runs, similarity results, and files.

Response `204`

---

### `GET /api/instructor/assignments/{assignmentId}/exclusion-code`

Response `200`:
```json
{ "assignmentId": "665f...", "exclusionCode": "starter template" }
```

---

### `PUT /api/instructor/assignments/{assignmentId}/exclusion-code`

Request:
```json
{ "exclusionCode": "starter template" }
```

Response `200`: `ExclusionCodeResponse`

---

### `DELETE /api/instructor/assignments/{assignmentId}/exclusion-code`

Clears exclusion code by setting it to `null`.

Response `200`:
```json
{ "assignmentId": "665f...", "exclusionCode": null }
```

Common admin errors:
- `401` invalid / missing token
- `403` assignment not owned by current instructor
- `404` assignment not found

---

## Public (no JWT)

### `POST /api/public/assignment-key/validate`

Request:
```json
{ "assignmentKey": "4829103756" }
```

Response `200` when valid:
```json
{
  "valid": true,
  "assignment": {
    "id": "665f...",
    "language": "java",
    "isOpen": true,
    "dueDate": "2025-06-08T23:59:59+00:00",
    "allowLate": false
  }
}
```

If key is unknown or expired:
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
| `studentEmail`      | string | no       |
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

Validation errors:
- `404` invalid assignment key
- `400` assignment key expired
- `400` assignment closed
- `400` due date passed and `allowLate=false`
- `400` invalid `studentEmail` format (when provided)
- `429` rate-limited (if enabled)

Notes:
- `studentEmail` is optional and non-blocking for submission success
- Email confirmation delivery may be disabled by provider configuration

---

## Runtime Behavior Notes

- Retention default: `DEFAULT_RETENTION_DAYS=30`; worker runs periodic purge for expired submissions and associated files.
- Anonymization applies to stored `studentIdentifier` when `ANONYMIZATION_MODE != none`.
- Rate limits are controlled by:
  - `RATE_LIMIT_AUTH_ATTEMPTS_PER_HOUR`
  - `RATE_LIMIT_SUBMISSION_ATTEMPTS_PER_HOUR`
  - `0` disables each scope.

---

## Removed Endpoints

The previous class-list scaffolding endpoints are removed and now return `404`:
- `GET /api/instructor/courses/{courseId}/class-list`
- `PUT /api/instructor/courses/{courseId}/class-list`
- `POST /api/instructor/courses/{courseId}/class-list`
