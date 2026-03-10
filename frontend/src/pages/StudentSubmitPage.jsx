import { useState } from 'react'
import { apiFetch } from '../services/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export default function StudentSubmitPage() {
  const [assignmentKey, setAssignmentKey] = useState('')
  const [keyError, setKeyError] = useState(null)
  const [keyLoading, setKeyLoading] = useState(false)
  const [validatedAssignment, setValidatedAssignment] = useState(null)
  const [studentIdentifier, setStudentIdentifier] = useState('')
  const [studentName, setStudentName] = useState('')
  const [zipFile, setZipFile] = useState(null)
  const [submitError, setSubmitError] = useState(null)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [confirmation, setConfirmation] = useState(null)

  async function handleValidateKey(e) {
    e.preventDefault()
    setKeyError(null)
    setKeyLoading(true)
    try {
      const data = await apiFetch('/public/assignment-key/validate', {
        method: 'POST', body: JSON.stringify({ assignmentKey }),
      })
      data.valid ? setValidatedAssignment(data.assignment) : setKeyError('Invalid assignment key.')
    } catch (err) { setKeyError(err.message) }
    finally { setKeyLoading(false) }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitError(null)
    setSubmitLoading(true)
    try {
      const fd = new FormData()
      fd.append('assignmentKey', assignmentKey)
      fd.append('studentIdentifier', studentIdentifier)
      if (studentName) fd.append('studentName', studentName)
      fd.append('zipFile', zipFile)
      const res = await fetch(`${API_BASE}/public/submissions`, { method: 'POST', body: fd })
      if (!res.ok) { const b = await res.json().catch(() => ({})); throw new Error(b.detail || `HTTP ${res.status}`) }
      setConfirmation(await res.json())
    } catch (err) { setSubmitError(err.message) }
    finally { setSubmitLoading(false) }
  }

  if (confirmation) return (
    <div className="min-h-screen bg-[#f0f0f4] flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-lg p-10 w-full max-w-sm text-center">
        <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-7 h-7 text-green-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Submission Received</h2>
        <p className="text-sm text-gray-500">ID: {confirmation.submissionId}</p>
        <p className="text-sm text-gray-500">Files: {confirmation.fileCount}</p>
      </div>
    </div>
  )

  const inputClass = "w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]/40"

  return (
    <div className="min-h-screen bg-[#f0f0f4] flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-lg p-10 w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[#3b3660] tracking-tight">Token Trail</h1>
          <p className="text-sm text-gray-500 mt-1">Submit Assignment</p>
        </div>
        {!validatedAssignment ? (
          <form onSubmit={handleValidateKey} className="flex flex-col gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">10-digit Assignment Key</label>
              <input type="text" value={assignmentKey} onChange={(e) => setAssignmentKey(e.target.value)}
                maxLength={10} required placeholder="e.g. 4829103756" className={inputClass}/>
            </div>
            {keyError && <p className="text-red-500 text-sm">{keyError}</p>}
            <button type="submit" disabled={keyLoading}
              className="bg-[#3b3660] text-white rounded-xl py-3 text-sm font-semibold hover:bg-[#2d2b4a] disabled:opacity-60 transition-colors">
              {keyLoading ? 'Validating…' : 'Validate Key'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <p className="text-sm text-gray-600 bg-gray-50 rounded-xl px-4 py-2.5">
              Language: <strong>{validatedAssignment.language?.toUpperCase()}</strong>
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Student Email / ID</label>
              <input type="text" value={studentIdentifier} onChange={(e) => setStudentIdentifier(e.target.value)}
                required placeholder="alice@uni.edu" className={inputClass}/>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name (optional)</label>
              <input type="text" value={studentName} onChange={(e) => setStudentName(e.target.value)}
                placeholder="Alice" className={inputClass}/>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ZIP File</label>
              <input type="file" accept=".zip" onChange={(e) => setZipFile(e.target.files[0])} required
                className="w-full text-sm text-gray-500 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-[#3b3660] file:text-white hover:file:bg-[#2d2b4a]"/>
            </div>
            {submitError && <p className="text-red-500 text-sm">{submitError}</p>}
            <button type="submit" disabled={submitLoading}
              className="bg-[#3b3660] text-white rounded-xl py-3 text-sm font-semibold hover:bg-[#2d2b4a] disabled:opacity-60 transition-colors">
              {submitLoading ? 'Submitting…' : 'Submit'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
