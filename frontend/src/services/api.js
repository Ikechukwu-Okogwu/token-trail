
/**
 * Base API fetch helper for Token Trail.
 * Reads VITE_API_BASE_URL and attaches the JWT when present.
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`
  const headers = { ...options.headers }

  const token = localStorage.getItem('token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(url, { ...options, headers })
  
  
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))

    if (res.status === 401) {
      localStorage.removeItem('token') 
      window.location.reload() //forcing reload on some protected will trigger the unauth splash screen
      return
    }

    const error = new Error(body.detail || `HTTP ${res.status}`)
    error.status = res.status
    throw error
  }

  if (res.status === 204) return null
  
  return res.json()
}

export default apiFetch

// --- Auth ---

export function login(email, password) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function signup(name, email, password) {
  return apiFetch('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  })
}

export function logout() {
  localStorage.removeItem('token')
  window.location.href = '/login'
}

// --- Student (no login needed) ---

export function validateAssignmentKey(assignmentKey) {
  return apiFetch('/public/assignment-key/validate', {
    method: 'POST',
    body: JSON.stringify({ assignmentKey }),
  })
}

export function submitAssignment({ assignmentKey, studentIdentifier, studentName, zipFile }) {
  const form = new FormData()
  form.append('assignmentKey', assignmentKey)
  form.append('studentIdentifier', studentIdentifier)
  if (studentName) form.append('studentName', studentName)
  form.append('zipFile', zipFile)

  return apiFetch('/public/submissions', {
    method: 'POST',
    body: form,
  })
}

// --- Instructor (login required) ---

export function getCourses() {
  return apiFetch('/instructor/courses')
}

export function listSubmissions(assignmentId) {
  return apiFetch(`/instructor/assignments/${assignmentId}/submissions`)
}

export function getInstructorAssignmentById(assignmentId) {
  return apiFetch(`/instructor/assignments/${assignmentId}`)
}

export function updateInstructorAssignment(assignmentId, body) {
  return apiFetch(`/instructor/assignments/${assignmentId}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  })
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

export function getInstructorCourses() {
  return apiFetch('/instructor/courses')
}

export function getCourseAssignments(courseId) {
  return apiFetch(`/instructor/courses/${courseId}/assignments`)
}

// --- Similarity results (instructor, login required) ---

export function getSimilarityResults(runId) {
  return apiFetch(`/instructor/analysis-runs/${runId}/similarity-results`)
}

export function getSimilarityPairDetail(resultId) {
  return apiFetch(`/instructor/similarity-results/${resultId}`)
}

export function getSimilarityComparison(resultId) {
  return apiFetch(`/instructor/similarity-results/${resultId}/comparison`)
}

// --- Repository import/export (instructor, login required) ---

export function importRepositoryZip(assignmentId, zipFile) {
  const form = new FormData()
  form.append('zipFile', zipFile)
  return apiFetch(`/instructor/assignments/${assignmentId}/submissions/import`, {
    method: 'POST',
    body: form,
  })
}

export async function downloadSubmissionsZip(assignmentId) {
  const url = `${API_BASE}/instructor/assignments/${assignmentId}/submissions/download`
  const headers = {}
  const token = localStorage.getItem('token')
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(url, { headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const error = new Error(body.detail || `HTTP ${res.status}`)
    error.status = res.status
    throw error
  }

  const blob = await res.blob()
  const disposition = res.headers.get('Content-Disposition') || ''
  const match = disposition.match(/filename="?([^"]+)"?/)
  const filename = match ? match[1] : `assignment-${assignmentId}-submissions.zip`

  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(a.href)
}