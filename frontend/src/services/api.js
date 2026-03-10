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

