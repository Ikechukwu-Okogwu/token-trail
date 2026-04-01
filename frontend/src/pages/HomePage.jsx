import { useState, useEffect, useRef } from 'react'
import { apiFetch } from '../services/api'
import CreateCourseForm from '../components/CreateCourseForm'
import Sidebar from '../components/Sidebar/Sidebar'
import { Link, useNavigate } from 'react-router-dom'
import {
  Search, Plus, LayoutGrid, List, AlertTriangle,
  Loader2, BookOpen, MoreVertical, Pencil, Trash2, ClipboardList, FlaskConical
} from 'lucide-react'
import Button from '../components/ui/Button'

export default function HomePage({ onCourseCreated }) {
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

  function handleCourseUpdated() {
    setRefreshKey((k) => k + 1)
  }

  const filtered = courses.filter((c) =>
    c.name?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="h-screen flex">
      <Sidebar refreshKey={refreshKey}/>
      <main className="ml-55 flex-1 overflow-y-auto bg-brand-pink/40">
        <div className="mx-auto max-w-5xl p-6 lg:p-8">

          {/* Page header */}
          <div className="mb-7 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-brand-purple/60">Instructor Dashboard</p>
              <h1 className="text-2xl font-bold text-gray-900">Courses</h1>
              <p className="mt-1 text-sm text-gray-400">Manage your courses and track assignment analysis.</p>
            </div>
            <Button onClick={() => setShowCreate(true)} size="lg">
              <Plus className="h-4 w-4" /> New Course
            </Button>
          </div>

          {/* Toolbar */}
          <div className="mb-6 flex items-center gap-3">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400 pointer-events-none" />
              <input
                type="text"
                placeholder="Search courses…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="h-10 w-full rounded-xl border border-gray-200 bg-white pl-10 pr-4 text-sm text-gray-700 placeholder-gray-400 shadow-sm outline-none transition focus:border-brand-purple/40 focus:ring-2 focus:ring-brand-purple/10"
              />
            </div>

            <div className="flex items-center rounded-xl border border-gray-200 bg-white p-1 shadow-sm">
              <button
                onClick={() => setViewMode('grid')}
                aria-label="Grid view"
                className={`rounded-lg p-2 transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-brand-purple text-white shadow-sm'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <LayoutGrid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                aria-label="List view"
                className={`rounded-lg p-2 transition-colors ${
                  viewMode === 'list'
                    ? 'bg-brand-purple text-white shadow-sm'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <List className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-6 flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span className="flex-1">{error}</span>
              <button
                onClick={() => setRefreshKey((k) => k + 1)}
                className="ml-auto font-medium text-red-600 underline hover:text-red-800"
              >
                Retry
              </button>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="flex items-center justify-center gap-2 py-24 text-sm text-gray-400">
              <Loader2 className="h-5 w-5 animate-spin" />
              Loading courses…
            </div>
          )}

          {/* Empty */}
          {!loading && !error && filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-purple/10">
                <BookOpen className="h-7 w-7 text-brand-purple/50" />
              </div>
              <p className="text-sm font-semibold text-gray-600">
                {search ? `No courses match "${search}"` : 'No courses yet'}
              </p>
              {!search && (
                <p className="mt-1.5 text-xs text-gray-400">
                  Create your first course to get started.
                </p>
              )}
              {!search && (
                <button
                  onClick={() => setShowCreate(true)}
                  className="mt-5 inline-flex items-center gap-2 rounded-xl bg-brand-purple px-4 py-2 text-sm font-semibold text-white transition hover:bg-purple-clicked"
                >
                  <Plus className="h-4 w-4" /> New Course
                </button>
              )}
            </div>
          )}

          {/* Course list/grid */}
          {!loading && !error && filtered.length > 0 && (
            <>
              {/* Section label */}
              <div className="mb-4 flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-widest text-gray-400">
                  Your Courses
                  <span className="ml-2 rounded-full bg-brand-purple/10 px-2 py-0.5 text-brand-purple normal-case tracking-normal">
                    {filtered.length}
                  </span>
                </p>
              </div>

              {viewMode === 'grid' ? (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {filtered.map((course) => (
                    <CourseCard key={course.id} course={course} onUpdated={handleCourseUpdated} />
                  ))}
                  {/* Ghost "add course" slot */}
                  <button
                    onClick={() => setShowCreate(true)}
                    className="flex min-h-[168px] flex-col items-center justify-center gap-2.5 rounded-2xl border-2 border-dashed border-gray-200 bg-transparent text-gray-400 transition-all duration-200 hover:border-brand-purple/40 hover:bg-brand-purple/[0.025] hover:text-brand-purple"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl border-2 border-dashed border-current/30 transition-colors">
                      <Plus className="h-5 w-5" />
                    </div>
                    <span className="text-xs font-semibold">New Course</span>
                  </button>
                </div>
              ) : (
                <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm divide-y divide-gray-100">
                  {filtered.map((course) => (
                    <CourseListItem key={course.id} course={course} onUpdated={handleCourseUpdated} />
                  ))}
                </div>
              )}
            </>
          )}

          {/* Create course modal */}
          {showCreate && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[2px]">
              <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl">
                <CreateCourseForm onCreated={handleCreated} onCancel={() => setShowCreate(false)} />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}


/* ── Course Card (grid view) with 3-dot menu ── */
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

  if (editing) {
    return (
      <div className="rounded-2xl border-2 border-brand-purple bg-white p-5">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-brand-purple">Edit Course</p>
        <div className="mb-2">
          <label htmlFor="edit-course-name" className="mb-1 block text-xs font-medium text-gray-600">Course Name</label>
          <input
            id="edit-course-name"
            type="text" value={editName}
            onChange={(e) => setEditName(e.target.value)}
            onClick={(e) => e.stopPropagation()}
            className="w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/30"
          />
        </div>
        <div className="mb-3">
          <label htmlFor="edit-course-term" className="mb-1 block text-xs font-medium text-gray-600">Term</label>
          <input
            id="edit-course-term"
            type="text" value={editTerm}
            onChange={(e) => setEditTerm(e.target.value)}
            onClick={(e) => e.stopPropagation()}
            className="w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple/30"
          />
        </div>
        {editError && <p className="mb-2 text-xs text-red-500">{editError}</p>}
        <div className="flex gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); setEditing(false); setEditError(null) }}
            className="flex-1 rounded-lg border border-gray-300 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50"
          >Cancel</button>
          <button
            onClick={handleSave} disabled={saving || !editName.trim()}
            className="flex-1 rounded-lg bg-brand-purple px-3 py-1.5 text-xs text-white hover:bg-purple-clicked disabled:opacity-50"
          >{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </div>
    )
  }

  if (confirmDelete) {
    return (
      <div className="rounded-2xl border-2 border-red-300 bg-white p-5">
        <p className="mb-1 text-sm font-semibold text-gray-900">Delete &ldquo;{course.name}&rdquo;?</p>
        <p className="mb-4 text-xs text-gray-500">This will permanently delete the course and all its assignments.</p>
        {editError && <p className="mb-2 text-xs text-red-500">{editError}</p>}
        <div className="flex gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); setConfirmDelete(false); setEditError(null) }}
            className="flex-1 rounded-lg border border-gray-300 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50"
          >Cancel</button>
          <button
            onClick={handleDelete} disabled={deleting}
            className="flex-1 rounded-lg bg-red-500 px-3 py-1.5 text-xs text-white hover:bg-red-600 disabled:opacity-50"
          >{deleting ? 'Deleting…' : 'Delete'}</button>
        </div>
      </div>
    )
  }

  const initial = (course.name || '?').charAt(0).toUpperCase()

  return (
    <Link
      to={`/course/${course.id}`}
      className="group block overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:shadow-xl hover:border-brand-purple/30 hover:-translate-y-1 no-underline"
    >
      {/* Colored top accent stripe */}
      <div className="h-1.5 w-full bg-brand-purple opacity-80" />

      <div className="p-5">
        {/* Card header: avatar + name + menu */}
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-purple/10 text-base font-bold text-brand-purple select-none">
              {initial}
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-bold text-gray-900 leading-tight">{course.name}</p>
              {course.term
                ? <span className="mt-1 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-[11px] font-medium text-gray-500">{course.term}</span>
                : <span className="mt-1 inline-block text-[11px] text-gray-400">No term set</span>
              }
            </div>
          </div>

          <div ref={menuRef} className="relative shrink-0">
            <button
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); setMenuOpen((o) => !o) }}
              className="rounded-lg p-1.5 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-700"
              aria-label="Options"
            >
              <MoreVertical className="h-4 w-4" />
            </button>

            {menuOpen && (
              <div
                role="menu"
                className="absolute right-0 top-8 z-20 w-36 overflow-hidden rounded-xl border border-gray-200 bg-white py-1 shadow-lg"
                onClick={(e) => e.stopPropagation()}
                onKeyDown={(e) => { if (e.key === 'Escape') setMenuOpen(false) }}
              >
                <button
                  onClick={(e) => { e.preventDefault(); setMenuOpen(false); setEditing(true) }}
                  className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Pencil className="h-3.5 w-3.5" /> Edit
                </button>
                <button
                  onClick={(e) => { e.preventDefault(); setMenuOpen(false); setConfirmDelete(true) }}
                  className="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <Trash2 className="h-3.5 w-3.5" /> Delete
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Divider */}
        <hr className="mb-4 border-gray-100" />

        {/* Stats */}
        <div className="flex gap-4">
          <div className="flex-1 rounded-xl bg-brand-purple/10 px-3 py-2.5">
            <div className="text-2xl font-bold text-brand-purple leading-none">{course.assignmentCount ?? 0}</div>
            <div className="mt-1 flex items-center gap-1 text-[11px] text-brand-purple/60">
              <ClipboardList className="h-3 w-3" />
              {course.assignmentCount === 1 ? 'Assignment' : 'Assignments'}
            </div>
          </div>
          <div className="flex-1 rounded-xl bg-brand-purple/10 px-3 py-2.5">
            <div className="text-2xl font-bold text-brand-purple leading-none">{course.analysisCompleteCount ?? 0}</div>
            <div className="mt-1 flex items-center gap-1 text-[11px] text-brand-purple/60">
              <FlaskConical className="h-3 w-3" />
              Analyses
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}


/* ── Course List Item (list view) ── */
function CourseListItem({ course }) {
  const initial = (course.name || '?').charAt(0).toUpperCase()

  return (
    <Link
      to={`/course/${course.id}`}
      className="flex items-center justify-between px-5 py-3.5 transition-colors hover:bg-brand-purple/[0.025] no-underline group"
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-purple/10 text-sm font-bold text-brand-purple select-none">
          {initial}
        </div>
        <div className="min-w-0">
          <span className="block truncate text-sm font-semibold text-gray-900 group-hover:text-brand-purple transition-colors">{course.name}</span>
          {course.term && (
            <span className="text-xs text-gray-400">{course.term}</span>
          )}
        </div>
      </div>
      <div className="flex items-center gap-6 shrink-0 ml-4">
        <div className="text-right">
          <div className="text-sm font-bold text-brand-purple">{course.assignmentCount ?? 0}</div>
          <div className="text-[11px] text-gray-400">assignments</div>
        </div>
        <div className="text-right">
          <div className="text-sm font-bold text-brand-purple">{course.analysisCompleteCount ?? 0}</div>
          <div className="text-[11px] text-gray-400">analyses</div>
        </div>
      </div>
    </Link>
  )
}
