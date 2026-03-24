import { useState } from 'react'
import { apiFetch } from '../services/api'

export default function CreateCourseForm({ onCreated, onCancel }) {
  const [name, setName]   = useState('')
  const [term, setTerm]   = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)

    // Duplicate name + term check
    try {
      const existing = await apiFetch('/instructor/courses')
      const duplicate = existing.some(
        (c) =>
          c.name.trim().toLowerCase() === name.trim().toLowerCase() &&
          c.term.trim().toLowerCase() === term.trim().toLowerCase()
      )
      if (duplicate) {
        setError(`A course named "${name}" already exists for term "${term}".`)
        return
      }
    } catch {
      // If fetch fails, proceed — backend will handle it
    }

    setLoading(true)
    try {
      const course = await apiFetch('/instructor/courses', {
        method: 'POST',
        body: JSON.stringify({ name: name.trim(), term: term.trim() }),
      })
      onCreated(course)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3 className="text-lg font-bold text-gray-900 mb-4">New Course</h3>

      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Course Name</label>
        <input
          type="text" value={name} onChange={(e) => setName(e.target.value)} required
          placeholder="e.g. COSC 4P02"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]"
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Term</label>
        <input
          type="text" value={term} onChange={(e) => setTerm(e.target.value)} required
          placeholder="e.g. Fall 2025"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]"
        />
      </div>

      {error && (
        <p className="text-red-500 text-sm mb-3 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <div className="flex gap-2 justify-end">
        <button type="button" onClick={onCancel}
          className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
          Cancel
        </button>
        <button type="submit" disabled={loading}
          className="px-4 py-2 text-sm text-white bg-[#3b3660] rounded-lg hover:bg-[#2d2b4a] disabled:opacity-50">
          {loading ? 'Creating…' : 'Create'}
        </button>
      </div>
    </form>
  )
}
