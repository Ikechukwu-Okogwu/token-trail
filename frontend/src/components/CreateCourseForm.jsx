import { useState } from 'react'
import { apiFetch } from '../services/api'
import Input from './ui/Input'
import Button from './ui/Button'
import ErrorBanner from './ui/ErrorBanner'

export default function CreateCourseForm({ onCreated, onCancel }) {
  const [name, setName]   = useState('')
  const [term, setTerm]   = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)

    try {
      const existing = await apiFetch('/instructor/courses')
      const duplicate = existing.some(
        (c) =>
          c.name.trim().toLowerCase() === name.trim().toLowerCase() &&
          (c.term ?? '').trim().toLowerCase() === term.trim().toLowerCase()
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
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <h3 className="text-lg font-semibold text-gray-900">New Course</h3>

      <ErrorBanner message={error} />

      <Input
        label="Course Name"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
        placeholder="e.g. COSC 4P02"
        disabled={loading}
      />

      <Input
        label="Term"
        type="text"
        value={term}
        onChange={(e) => setTerm(e.target.value)}
        placeholder="e.g. Fall 2025 (optional)"
        disabled={loading}
      />

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
