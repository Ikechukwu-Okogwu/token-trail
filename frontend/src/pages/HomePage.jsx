import { useState, useEffect, useRef } from 'react'
import { apiFetch } from '../services/api'
import CreateCourseForm from '../components/CreateCourseForm'
import Sidebar from '../components/Sidebar/Sidebar'
import { Link, useNavigate } from 'react-router-dom'


/**
 * HomePage — instructor home, grid of course cards.
 * Fetches real courses from GET /api/instructor/courses.
 *
 * API response shape per course:
 *   { id, name, term, instructorId, createdAt }
 */

export default function HomePage({ onCourseCreated, onLogout }) {
  const [courses, setCourses]     = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)
  const [search, setSearch]       = useState('')
  const [viewMode, setViewMode]   = useState('grid')
  const [showCreate, setShowCreate] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    setError(null)
    apiFetch('/instructor/courses')
      .then((data) => setCourses(Array.isArray(data) ? data : []))
      .catch((err) => setError(err.message || 'Failed to load courses.'))
      .finally(() => setLoading(false))
  }, [refreshKey])

  function handleCreated(course) {
    setShowCreate(false)
    setRefreshKey((k) => k + 1)
    onCourseCreated?.()
    navigate(`/course/${course.id}`)
  }

  // Called by CourseCard after rename or delete
  function handleCourseUpdated() {
    setRefreshKey((k) => k + 1)
  }

  const filtered = courses.filter((c) =>
    c.name?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="h-screen flex">
      <Sidebar refreshKey={refreshKey}/>
      <main className="ml-55 flex-1">
        <div className="p-6 min-h-full">
          <div className="bg-white rounded-2xl shadow-sm p-6 min-h-full">

            {/* Toolbar */}
            <div className="flex items-center gap-3 mb-6">
              <div className="flex-1 flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-2.5">
                <svg style={{ display: 'block', width: 16, height: 16, flexShrink: 0 }}
                  className="text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h7"/>
                </svg>
                <input
                  type="text" placeholder="Search courses…" value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="flex-1 bg-transparent text-sm text-gray-600 placeholder-gray-400 outline-none"
                />
                <svg style={{ display: 'block', width: 16, height: 16, flexShrink: 0 }}
                  className="text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                </svg>
              </div>

              <div className="flex items-center bg-gray-100 rounded-xl p-1">
                <button onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-white shadow-sm text-gray-800' : 'text-gray-400 hover:text-gray-600'}`}>
                  <svg style={{ display: 'block', width: 16, height: 16 }}
                    fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                  </svg>
                </button>
                <button onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-white shadow-sm text-gray-800' : 'text-gray-400 hover:text-gray-600'}`}>
                  <svg style={{ display: 'block', width: 16, height: 16 }}
                    fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <rect x="3" y="3" width="7" height="7" rx="1"/>
                    <rect x="14" y="3" width="7" height="7" rx="1"/>
                    <rect x="3" y="14" width="7" height="7" rx="1"/>
                    <rect x="14" y="14" width="7" height="7" rx="1"/>
                  </svg>
                </button>
              </div>

              <div className="w-px h-8 bg-gray-200"/>

              <button onClick={() => setShowCreate(true)}
                className="flex items-center gap-2 bg-[#3b3660] text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-[#2d2b4a] transition-colors shadow-sm">
                <svg style={{ display: 'block', width: 16, height: 16 }}
                  fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4"/>
                </svg>
                New
              </button>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 mb-6 text-sm">
                <svg style={{ display: 'block', width: 18, height: 18, flexShrink: 0 }}
                  fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round"
                    d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                </svg>
                <span>{error}</span>
                <button onClick={() => setRefreshKey((k) => k + 1)}
                  className="ml-auto underline text-red-600 hover:text-red-800 font-medium">Retry</button>
              </div>
            )}

            {/* Loading */}
            {loading && (
              <div className="flex items-center justify-center gap-2 text-gray-400 text-sm py-16">
                <svg className="animate-spin" style={{ width: 18, height: 18 }} fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Loading courses…
              </div>
            )}

            {/* Empty */}
            {!loading && !error && filtered.length === 0 && (
              <div className="text-gray-400 text-sm text-center py-16">
                {search ? `No courses match "${search}"` : 'No courses yet — click + New to create one.'}
              </div>
            )}

            {/* Course cards */}
            {!loading && !error && filtered.length > 0 && (
              <div className={viewMode === 'grid' ? 'grid grid-cols-3 gap-4' : 'flex flex-col gap-3'}>
                {filtered.map((course) => (
                  <CourseCard key={course.id} course={course} onUpdated={handleCourseUpdated} />
                ))}
              </div>
            )}
          </div>

          {/* Create course modal */}
          {showCreate && (
            <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
              <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md">
                <CreateCourseForm onCreated={handleCreated} onCancel={() => setShowCreate(false)} />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

/* ── Course Card with 3-dot menu ── */
function CourseCard({ course, onUpdated }) {
  const [menuOpen, setMenuOpen]   = useState(false)
  const [editing, setEditing]     = useState(false)
  const [editName, setEditName]   = useState(course.name)
  const [editTerm, setEditTerm]   = useState(course.term || '')
  const [saving, setSaving]       = useState(false)
  const [editError, setEditError] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting]   = useState(false)
  const menuRef = useRef(null)
  const navigate = useNavigate()

  // Close menu when clicking outside
  useEffect(() => {
    function handleClick(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  async function handleSave(e) {
    e.preventDefault()
    e.stopPropagation()
    setEditError(null)
    setSaving(true)
    try {
      await apiFetch(`/instructor/courses/${course.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ name: editName.trim(), term: editTerm.trim() }),
      })
      setEditing(false)
      onUpdated()
    } catch (err) {
      setEditError(err.message || 'Failed to update course.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(e) {
    e.preventDefault()
    e.stopPropagation()
    setDeleting(true)
    try {
      await apiFetch(`/instructor/courses/${course.id}`, { method: 'DELETE' })
      onUpdated()
      navigate('/dashboard')
    } catch (err) {
      setEditError(err.message || 'Failed to delete course.')
      setConfirmDelete(false)
    } finally {
      setDeleting(false)
    }
  }

  // ── Editing mode — inline on the card ──
  if (editing) {
    return (
      <div className="bg-white border-2 border-[#3b3660] rounded-2xl p-5">
        <p className="text-xs font-semibold text-[#3b3660] uppercase tracking-wide mb-3">Edit Course</p>
        <div className="mb-2">
          <label className="block text-xs font-medium text-gray-600 mb-1">Course Name</label>
          <input
            type="text" value={editName}
            onChange={(e) => setEditName(e.target.value)}
            onClick={(e) => e.stopPropagation()}
            className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]"
          />
        </div>
        <div className="mb-3">
          <label className="block text-xs font-medium text-gray-600 mb-1">Term</label>
          <input
            type="text" value={editTerm}
            onChange={(e) => setEditTerm(e.target.value)}
            onClick={(e) => e.stopPropagation()}
            className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]"
          />
        </div>
        {editError && <p className="text-red-500 text-xs mb-2">{editError}</p>}
        <div className="flex gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); setEditing(false); setEditError(null) }}
            className="flex-1 px-3 py-1.5 text-xs text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
          >Cancel</button>
          <button
            onClick={handleSave} disabled={saving || !editName.trim()}
            className="flex-1 px-3 py-1.5 text-xs text-white bg-[#3b3660] rounded-lg hover:bg-[#2d2b4a] disabled:opacity-50"
          >{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </div>
    )
  }

  // ── Delete confirmation ──
  if (confirmDelete) {
    return (
      <div className="bg-white border-2 border-red-300 rounded-2xl p-5">
        <p className="text-sm font-semibold text-gray-900 mb-1">Delete "{course.name}"?</p>
        <p className="text-xs text-gray-500 mb-4">This will permanently delete the course and all its assignments.</p>
        {editError && <p className="text-red-500 text-xs mb-2">{editError}</p>}
        <div className="flex gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); setConfirmDelete(false); setEditError(null) }}
            className="flex-1 px-3 py-1.5 text-xs text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
          >Cancel</button>
          <button
            onClick={handleDelete} disabled={deleting}
            className="flex-1 px-3 py-1.5 text-xs text-white bg-red-500 rounded-lg hover:bg-red-600 disabled:opacity-50"
          >{deleting ? 'Deleting…' : 'Delete'}</button>
        </div>
      </div>
    )
  }

  // ── Normal card ──
  return (
    <div className="relative">
      <Link
        to={`/course/${course.id}`}
        className="bg-white border border-gray-200 rounded-2xl p-5 block hover:shadow-md hover:border-gray-300 transition-all group no-underline"
      >
        <div className="flex items-start justify-between mb-3">
          <span className="text-base font-bold text-gray-900">{course.name}</span>
          {/* 3-dot menu button */}
          <div ref={menuRef} className="relative">
            <button
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); setMenuOpen((o) => !o) }}
              className="text-gray-400 hover:text-gray-700 text-lg leading-none px-1 rounded hover:bg-gray-100 transition-colors"
              aria-label="Options"
            >⋮</button>

            {/* Dropdown */}
            {menuOpen && (
              <div className="absolute right-0 top-7 z-20 bg-white border border-gray-200 rounded-xl shadow-lg py-1 w-36"
                onClick={(e) => e.stopPropagation()}>
                <button
                  onClick={(e) => { e.preventDefault(); setMenuOpen(false); setEditing(true) }}
                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <svg style={{ width: 14, height: 14 }} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 012.828 2.828L11.828 15.828a2 2 0 01-2.828 0L9 13z"/>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 21h18"/>
                  </svg>
                  Edit
                </button>
                <button
                  onClick={(e) => { e.preventDefault(); setMenuOpen(false); setConfirmDelete(true) }}
                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <svg style={{ width: 14, height: 14 }} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>
        <hr className="border-gray-100 mb-4"/>
        <div className="flex gap-6">
          <div>
            <div className="text-3xl font-bold text-gray-900">{course.assignmentCount ?? 0}</div>
            <div className="text-xs text-gray-500 mt-0.5">
              {course.assignmentCount === 1 ? 'Assignment' : 'Assignments'}
            </div>
          </div>
          <div>
            <div className="text-3xl font-bold text-gray-900">{course.analysisCompleteCount ?? 0}</div>
            <div className="text-xs text-gray-500 mt-0.5">Analyses Complete</div>
          </div>
        </div>
        {course.term && (
          <div className="text-xs text-gray-400 mt-3 pt-3 border-t border-gray-100">{course.term}</div>
        )}
      </Link>
    </div>
  )
}
