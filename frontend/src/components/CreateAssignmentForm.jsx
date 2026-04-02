import { useState, useEffect } from 'react'
import { apiFetch } from '../services/api'
import Input from './ui/Input'
import Button from './ui/Button'
import ErrorBanner from './ui/ErrorBanner'

const LANGUAGES = ['java', 'c', 'cpp']

export default function CreateAssignmentForm({ courseId, onCreated, onCancel }) {
  const [title, setTitle]       = useState('')
  const [language, setLanguage] = useState('java')
  const [isOpen, setIsOpen]     = useState(true)
  const [dueDate, setDueDate]   = useState('')
  const [allowLate, setAllowLate] = useState(false)
  const [error, setError]       = useState(null)
  const [loading, setLoading]   = useState(false)

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
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <h3 className="text-lg font-semibold text-gray-900">New Assignment</h3>

      <ErrorBanner message={error} />

      <Input
        label="Title"
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
        placeholder="e.g. Assignment 1"
        disabled={loading}
      />

      <div>
        <label htmlFor="assignment-language" className="mb-1 block text-sm font-medium text-gray-700">Language</label>
        <select
          id="assignment-language"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          disabled={loading}
          className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/30"
        >
          {LANGUAGES.map((l) => <option key={l} value={l}>{l.toUpperCase()}</option>)}
        </select>
      </div>

      <div>
        <label htmlFor="assignment-due" className="mb-1 block text-sm font-medium text-gray-700">Due Date (optional)</label>
        <input
          id="assignment-due"
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          disabled={loading}
          className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/30"
        />
        {isPastDue && (
          <p className="mt-1 text-xs text-amber-600">
            Due date is in the past — Open for submissions set to No.
          </p>
        )}
      </div>

      <div>
        <span className="mb-1 block text-sm font-medium text-gray-700">Open for Submissions</span>
        <div className="flex gap-4">
          <label className="flex cursor-pointer items-center gap-1.5 text-sm">
            <input type="radio" name="isOpen" checked={isOpen === true}
              onChange={() => setIsOpen(true)}
              disabled={isPastDue || loading}
              className="accent-brand-purple"/>
            Yes
          </label>
          <label className="flex cursor-pointer items-center gap-1.5 text-sm">
            <input type="radio" name="isOpen" checked={isOpen === false}
              onChange={() => setIsOpen(false)}
              disabled={loading}
              className="accent-brand-purple"/>
            No
          </label>
        </div>
      </div>

      <div>
        <span className="mb-1 block text-sm font-medium text-gray-700">Allow Late Submissions</span>
        <div className="flex gap-4">
          <label className="flex cursor-pointer items-center gap-1.5 text-sm">
            <input type="radio" name="allowLate" checked={allowLate === true}
              onChange={() => setAllowLate(true)}
              disabled={loading}
              className="accent-brand-purple"/>
            Yes
          </label>
          <label className="flex cursor-pointer items-center gap-1.5 text-sm">
            <input type="radio" name="allowLate" checked={allowLate === false}
              onChange={() => setAllowLate(false)}
              disabled={loading}
              className="accent-brand-purple"/>
            No
          </label>
        </div>
      </div>

      <div className="flex gap-2 justify-end pt-1">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? 'Creating…' : 'Create'}
        </Button>
      </div>
    </form>
  )
}
