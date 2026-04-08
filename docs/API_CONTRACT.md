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

Response `200`:
```json
{
  "runId": "665f...",
  "assignmentId": "665f...",
  "results": [
    {
      "resultId": "665f...__leftSubmissionId__rightSubmissionId",
      "runId": "665f...",
      "assignmentId": "665f...",
      "leftSubmissionId": "665f...",
      "leftStudentIdentifier": "student-1",
      "leftStudentName": "student-1",
      "rightSubmissionId": "665f...",
      "rightStudentIdentifier": "student-2",
      "rightStudentName": "student-2",
      "similarityScore": 0.87,
      "confidence": 0.84,
      "largestBlockSize": 12,
      "analysisMethod": "tokenize",
      "warnings": []
    }
  ]
}
```

Notes:
- `resultId` format is `runId__leftSubmissionId__rightSubmissionId`.
- `analysisMethod` is currently `tokenize` or `error_fallback`.
- `warnings` may include parse-quality warnings or pipeline-error messages captured during worker execution.

---

### `GET /api/instructor/similarity-results/{resultId}`

Response `200`:
```json
{
  "resultId": "665f...__leftSubmissionId__rightSubmissionId",
  "runId": "665f...",
  "assignmentId": "665f...",
  "leftSubmissionId": "665f...",
  "leftStudentIdentifier": "student-1",
  "leftStudentName": "student-1",
  "rightSubmissionId": "665f...",
  "rightStudentIdentifier": "student-2",
  "rightStudentName": "student-2",
  "similarityScore": 0.87,
  "summary": "Pair similarity computed from merged submission sources."
}
```

---

### `GET /api/instructor/similarity-results/{resultId}/comparison`

Response `200`:
```json
{
  "resultId": "665f...__leftSubmissionId__rightSubmissionId",
  "runId": "665f...",
  "assignmentId": "665f...",
  "leftSubmissionId": "665f...",
  "leftStudentIdentifier": "student-1",
  "leftStudentName": "student-1",
  "rightSubmissionId": "665f...",
  "rightStudentIdentifier": "student-2",
  "rightStudentName": "student-2",
  "similarityScore": 0.87,
  "leftFilePath": "uploads/.../merged/merged.txt",
  "rightFilePath": "uploads/.../merged/merged.txt",
  "leftCode": "//// FILE: ...",
  "rightCode": "//// FILE: ...",
  "matchingRegions": [
    {
      "leftStartLine": 10,
      "leftEndLine": 18,
      "rightStartLine": 11,
      "rightEndLine": 19,
      "score": 0.42,
      "evidenceType": "tokenize_group",
      "snippet": "for (...) { ... }"
    }
  ],
  "excludedRegions": [
    {
      "leftStartLine": 1,
      "leftEndLine": 9,
      "rightStartLine": null,
      "rightEndLine": null,
      "evidenceType": "non_match",
      "reason": "No matching fingerprint group"
    }
  ],
  "summary": "Detected 1 matched block(s) with similarity score 87.00%.",
  "confidence": 0.84,
  "snippets": ["for (...) { ... }"],
  "analysisMethod": "tokenize",
  "warnings": []
}
```

Notes:
- `matchingRegions[].evidenceType` is usually `tokenize_group` or `winnowing_group`.
- Comparison responses may be recomputed at read time when full persisted comparison fields are unavailable.
- Current known behavior: recomputation does not pass assignment `exclusionCode`, so template-heavy assignments can show regions/snippets that do not perfectly align with the stored pair score.

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

### `POST /api/instructor/assignments/{assignmentId}/submissions/import`

Imports a repository ZIP into an assignment.

Accepted outer ZIP layouts:
- flat zip-of-zips: top-level `StudentA.zip`, `StudentB.zip`, ...
- exported layout: `<folder>/raw.zip` per submission

Response `201`:
```json
{
  "imported": 2,
  "skipped": 1,
  "details": [
    { "folder": "StudentA", "submissionId": "665f...", "fileCount": 3 }
  ],
  "skippedDetails": [
    { "folder": "StudentB", "reason": "Duplicate: a submission with this identifier already exists" }
  ]
}
```

The submission identifier is derived from the inner zip filename or folder name.

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
- `422` merged submission appears not to contain valid code for the assignment language
- `429` rate-limited (if enabled)

Notes:
- `studentEmail` is optional and non-blocking for submission success
- Email confirmation delivery may be disabled by provider configuration
- The `422` path is based on a quick parse-quality check on merged source and is intended to reject obvious language mismatches (for example, non-Java code inside a `.java` submission).

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
