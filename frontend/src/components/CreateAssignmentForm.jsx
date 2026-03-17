import { useState } from 'react'
import { apiFetch } from '../services/api'

const LANGUAGES = ['java', 'c', 'cpp']

export default function CreateAssignmentForm({ courseId, onCreated, onCancel }) {
  const [title, setTitle] = useState('')
  const [language, setLanguage] = useState('java')
  const [isOpen, setIsOpen] = useState(true)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const assignment = await apiFetch('/instructor/assignments', {
        method: 'POST',
        body: JSON.stringify({ courseId, title, language, isOpen }),
      })
      onCreated(assignment)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3 className="text-lg font-bold text-gray-900 mb-4">New Assignment</h3>
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
        <input
          type="text" value={title} onChange={(e) => setTitle(e.target.value)} required
          placeholder="e.g. Assignment 1"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]"
        />
      </div>
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]">
          {LANGUAGES.map((l) => <option key={l} value={l}>{l.toUpperCase()}</option>)}
        </select>
      </div>
      <div className="mb-4">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 cursor-pointer">
          <input type="checkbox" checked={isOpen} onChange={(e) => setIsOpen(e.target.checked)}
            className="rounded border-gray-300"/>
          Open for submissions
        </label>
      </div>
      {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
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
