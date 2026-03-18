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

  //If the server returned an error, throw it so we can show an error message
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${res.status}`)
    error.status = re.status
    throw error
  }

  //Return the server's response as a JavaScript object
  return res.json()
  
}
export default apiFetch

//-Authorization Function-

export function login (email, password){
  return apiFetch ('/auth/login', { method: 'POST', body: JSON.stringify ({email, password}),
  })
}
//Create a new instructor account
export function signup(name, email, password) {
  return apiFetch('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  })
}
//Log out — removes the token and sends user to login page
export function logout() {
  localStorage.removeItem('token')
  window.location.href = '/login'
}
  
 // student function , no login needed
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
  //Instructor Functions, login required 
// Get list of courses for the logged-in instructor
export function getCourses() {
  return apiFetch('/instructor/courses')
}

//Gets lisst of submissions for an assignment
export function listSubmissions(assignmentId) {
  return apiFetch(`/instructor/assignments/${assignmentId}/submissions`)
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
