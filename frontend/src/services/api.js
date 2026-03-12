/**
 * Base API fetch helper for Token Trail.
 * Reads VITE_API_BASE_URL and attaches the JWT when present.
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`
  const headers = { ...options.headers }

  // Attach JWT from localStorage if available
  const token = localStorage.getItem('token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Auto-set JSON content-type unless body is FormData
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(url, { ...options, headers })

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }

  return res.json()
}

export function getInstructorAssignmentById(assignmentId) {
  return apiFetch(`/instructor/assignments/${assignmentId}`)
}

export function getAssignmentSubmissions(assignmentId) {
  return apiFetch(`/instructor/assignments/${assignmentId}/submissions`)
}

export function queueAnalysisRun(assignmentId) {
  return apiFetch(`/instructor/assignments/${assignmentId}/analysis-runs`, {
    method: 'POST',
  })
}

export function getAnalysisRunStatus(runId) {
  return apiFetch(`/instructor/analysis-runs/${runId}`)
}

/**
 * Get ranked similarity results for an analysis run.
 * TODO: Backend returns 501 until implemented.
 * Expected response shape: { runId, results: [{ resultId, leftSubmissionId, rightSubmissionId, similarityScore, matchingLineCount?, leftStudentName?, rightStudentName? }] }
 * Sorted descending by similarity score (per SRS 4.3.2).
 */
export function getSimilarityResults(runId) {
  return apiFetch(`/instructor/analysis-runs/${runId}/similarity-results`)
}

/**
 * Get side-by-side comparison for a similarity result.
 * TODO: Backend returns 501 until implemented.
 * Expected response shape: { resultId, leftFilePath, rightFilePath, matchingRegions: [{ leftStartLine, leftEndLine, rightStartLine, rightEndLine }], leftContent?, rightContent? }
 * (per SRS 4.3.3 and Data Dictionary)
 */
export function getSimilarityComparison(resultId) {
  return apiFetch(`/instructor/similarity-results/${resultId}/comparison`)
}
