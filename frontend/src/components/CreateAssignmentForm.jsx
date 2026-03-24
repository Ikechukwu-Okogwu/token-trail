import { useState, useEffect } from 'react'
import { apiFetch } from '../services/api'

const LANGUAGES = ['java', 'c', 'cpp']

export default function CreateAssignmentForm({ courseId, onCreated, onCancel }) {
  const [title, setTitle]       = useState('')
  const [language, setLanguage] = useState('java')
  const [isOpen, setIsOpen]     = useState(true)
  const [dueDate, setDueDate]   = useState('')
  const [allowLate, setAllowLate] = useState(false)
  const [error, setError]       = useState(null)
  const [loading, setLoading]   = useState(false)

  // Auto-set isOpen to false when due date is in the past
  useEffect(() => {
    if (dueDate) {
      const due = new Date(dueDate)
      const now = new Date()
      if (due < now) setIsOpen(false)
    }
  }, [dueDate])

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)

    // Duplicate title check
    try {
      const existing = await apiFetch(`/instructor/courses/${courseId}/assignments`)
      const duplicate = existing.some(
        (a) => a.title.trim().toLowerCase() === title.trim().toLowerCase()
      )
      if (duplicate) {
        setError(`An assignment named "${title}" already exists in this course.`)
        return
      }
    } catch {
      // If fetch fails, proceed anyway — backend will catch it
    }

    setLoading(true)
    try {
      const body = {
        courseId,
        title: title.trim(),
        language,
        isOpen,
        allowLate,
        dueDate: dueDate || null,
      }
      const assignment = await apiFetch('/instructor/assignments', {
        method: 'POST',
        body: JSON.stringify(body),
      })
      onCreated(assignment)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const isPastDue = dueDate && new Date(dueDate) < new Date()

  return (
    <form onSubmit={handleSubmit}>
      <h3 className="text-lg font-bold text-gray-900 mb-4">New Assignment</h3>

      {/* Title */}
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
        <input
          type="text" value={title} onChange={(e) => setTitle(e.target.value)} required
          placeholder="e.g. Assignment 1"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]"
        />
      </div>

      {/* Language */}
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]">
          {LANGUAGES.map((l) => <option key={l} value={l}>{l.toUpperCase()}</option>)}
        </select>
      </div>

      {/* Due Date */}
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Due Date (optional)</label>
        <input
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]"
        />
        {isPastDue && (
          <p className="text-xs text-amber-600 mt-1">
            ⚠ Due date is in the past — Open for submissions set to No.
          </p>
        )}
      </div>

      {/* Open for submissions */}
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Open for Submissions</label>
        <div className="flex gap-4">
          <label className="flex items-center gap-1.5 text-sm cursor-pointer">
            <input type="radio" name="isOpen" checked={isOpen === true}
              onChange={() => setIsOpen(true)}
              disabled={isPastDue}
              className="accent-[#3b3660]"/>
            Yes
          </label>
          <label className="flex items-center gap-1.5 text-sm cursor-pointer">
            <input type="radio" name="isOpen" checked={isOpen === false}
              onChange={() => setIsOpen(false)}
              className="accent-[#3b3660]"/>
            No
          </label>
        </div>
      </div>

      {/* Allow Late */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Allow Late Submissions</label>
        <div className="flex gap-4">
          <label className="flex items-center gap-1.5 text-sm cursor-pointer">
            <input type="radio" name="allowLate" checked={allowLate === true}
              onChange={() => setAllowLate(true)}
              className="accent-[#3b3660]"/>
            Yes
          </label>
          <label className="flex items-center gap-1.5 text-sm cursor-pointer">
            <input type="radio" name="allowLate" checked={allowLate === false}
              onChange={() => setAllowLate(false)}
              className="accent-[#3b3660]"/>
            No
          </label>
        </div>
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
