import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { apiFetch } from '../services/api'
import CreateAssignmentForm from '../components/CreateAssignmentForm'
import Sidebar from '../components/Sidebar/Sidebar'
import Button from '../components/ui/Button'
import {
  Search, Plus, LayoutGrid, List, AlertTriangle,
  Loader2, FileCode, Calendar, ArrowLeft,
  Users, FlaskConical, Clock, ChevronRight,
} from 'lucide-react'

function formatDueDate(value) {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

function isOverdue(value) {
  if (!value) return false
  const date = new Date(value)
  return !Number.isNaN(date.getTime()) && date < new Date()
}

const LANG_COLORS = {
  java:  'bg-orange-100 text-orange-700',
  c:     'bg-blue-100 text-blue-700',
  cpp:   'bg-violet-100 text-violet-700',
  'c++': 'bg-violet-100 text-violet-700',
}

export default function CoursePage({ onAssignmentCreated }) {
  const { courseId } = useParams()
  const [course, setCourse]           = useState(null)
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState(null)
  const [search, setSearch]           = useState('')
  const [viewMode, setViewMode]       = useState('grid')
  const [showCreate, setShowCreate]   = useState(false)
  const [refreshKey, setRefreshKey]   = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    if (!courseId) return
    setLoading(true)
    setError(null)
    Promise.all([
      apiFetch(`/instructor/courses/${courseId}/assignments`),
      apiFetch(`/instructor/courses/${courseId}`).catch(() => null),
    ])
      .then(([assignmentData, courseData]) => {
        setAssignments(Array.isArray(assignmentData) ? assignmentData : [])
        setCourse(courseData)
      })
      .catch((err) => setError(err.message || 'Failed to load assignments.'))
      .finally(() => setLoading(false))
  }, [courseId, refreshKey])

  function handleCreated(assignment) {
    setShowCreate(false)
    setRefreshKey((k) => k + 1)
    onAssignmentCreated?.()
    navigate(`/course/${courseId}/assignment/${assignment.id}`)
  }

  const filtered = assignments.filter((a) =>
    a.title?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="h-screen flex">
      <Sidebar refreshKey={refreshKey} />
      <main className="ml-55 flex-1 overflow-y-auto bg-brand-pink/40">
        <div className="mx-auto max-w-5xl p-6 lg:p-8">

          {/* Breadcrumb */}
          <Link
            to="/dashboard"
            className="mb-3 inline-flex items-center gap-1.5 text-sm text-gray-400 no-underline transition-colors hover:text-brand-purple"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Dashboard
          </Link>

          {/* Page header */}
          <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              {course?.name && (
                <>
                  <h1 className="text-2xl font-bold text-gray-900">
                    {course.name}
                  </h1>
                  <p className="mt-1 text-sm text-gray-400">
                    {course.term ? `${course.term}` : ''}
                  </p>
                </>
              )}
              
            </div>
            <Button onClick={() => setShowCreate(true)} size="lg">
              <Plus className="h-4 w-4" /> New Assignment
            </Button>
          </div>

          {/* Toolbar */}
          <div className="mb-6 flex items-center gap-3">
            <div className="relative flex-1 max-w-sm">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search assignments…"
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
                  viewMode === 'grid' ? 'bg-brand-purple text-white shadow-sm' : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <LayoutGrid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                aria-label="List view"
                className={`rounded-lg p-2 transition-colors ${
                  viewMode === 'list' ? 'bg-brand-purple text-white shadow-sm' : 'text-gray-400 hover:text-gray-600'
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
              Loading assignments…
            </div>
          )}

          {/* Empty */}
          {!loading && !error && filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-purple/10">
                <FileCode className="h-7 w-7 text-brand-purple/50" />
              </div>
              <p className="text-sm font-semibold text-gray-600">
                {search ? `No assignments match "${search}"` : 'No assignments yet'}
              </p>
              {!search && (
                <>
                  <p className="mt-1.5 text-xs text-gray-400">
                    Create your first assignment to start collecting submissions.
                  </p>
                  <button
                    onClick={() => setShowCreate(true)}
                    className="mt-5 inline-flex items-center gap-2 rounded-xl bg-brand-purple px-4 py-2 text-sm font-semibold text-white transition hover:bg-purple-clicked"
                  >
                    <Plus className="h-4 w-4" /> New Assignment
                  </button>
                </>
              )}
            </div>
          )}

          {/* Assignments grid/list */}
          {!loading && !error && filtered.length > 0 && (
            <>
              {/* Section label */}
              <div className="mb-4">
                <p className="text-xs font-semibold uppercase tracking-widest text-gray-400">
                  Your Assignments
                  <span className="ml-2 rounded-full bg-brand-purple/10 px-2 py-0.5 normal-case tracking-normal text-brand-purple">
                    {filtered.length}
                  </span>
                </p>
              </div>

              {viewMode === 'grid' ? (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {filtered.map((a) => (
                    <AssignmentCard key={a.id} assignment={a} courseId={courseId} />
                  ))}
                  {/* Ghost slot */}
                  <button
                    onClick={() => setShowCreate(true)}
                    className="flex min-h-[168px] flex-col items-center justify-center gap-2.5 rounded-2xl border-2 border-dashed border-gray-200 bg-transparent text-gray-400 transition-all duration-200 hover:border-brand-purple/40 hover:bg-brand-purple/[0.025] hover:text-brand-purple"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl border-2 border-dashed border-current/30">
                      <Plus className="h-5 w-5" />
                    </div>
                    <span className="text-xs font-semibold">New Assignment</span>
                  </button>
                </div>
              ) : (
                <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm divide-y divide-gray-100">
                  {filtered.map((a) => (
                    <AssignmentListItem key={a.id} assignment={a} courseId={courseId} />
                  ))}
                </div>
              )}
            </>
          )}

          {/* Create assignment modal */}
          {showCreate && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[2px]">
              <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl">
                <CreateAssignmentForm
                  courseId={courseId}
                  onCreated={handleCreated}
                  onCancel={() => setShowCreate(false)}
                />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}


/* ── Assignment Card (grid view) ── */
function AssignmentCard({ assignment, courseId }) {
  const isOpen    = assignment.isOpen
  const overdue   = isOverdue(assignment.dueDate)
  const langClass = LANG_COLORS[assignment.language?.toLowerCase()] || 'bg-gray-100 text-gray-600'
  const hasAnalysis = assignment.analysisProgress != null

  return (
    <Link
      to={`/course/${courseId}/assignment/${assignment.id}`}
      className="group block overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:shadow-xl hover:border-brand-purple/30 hover:-translate-y-1 no-underline"
    >
      {/* Top accent stripe */}
      <div className={`h-1.5 w-full ${isOpen ? 'bg-brand-purple opacity-80' : 'bg-gray-300'}`} />

      <div className="p-5">
        {/* Title + badges */}
        <div className="mb-1 flex items-start justify-between gap-2">
          <h3 className="text-sm font-bold text-gray-900 leading-snug line-clamp-2 flex-1">
            {assignment.title}
          </h3>
          <span className={`mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold ${
            isOpen ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-500'
          }`}>
            {isOpen ? 'Open' : 'Closed'}
          </span>
        </div>

        {assignment.language && (
          <span className={`inline-block rounded-full px-2 py-0.5 text-[11px] font-medium ${langClass}`}>
            {assignment.language.toUpperCase()}
          </span>
        )}

        <hr className="my-4 border-gray-100" />

        {/* Stats tiles */}
        <div className="flex gap-3">
          <div className="flex-1 rounded-xl bg-brand-purple/10 px-3 py-2.5">
            <div className="text-2xl font-bold text-brand-purple leading-none">
              {assignment.submissionCount ?? 0}
            </div>
            <div className="mt-1 flex items-center gap-1 text-[11px] text-brand-purple/60">
              <Users className="h-3 w-3" /> Submissions
            </div>
          </div>
          <div className="flex-1 rounded-xl bg-brand-purple/10 px-3 py-2.5">
            <div className={`text-2xl font-bold leading-none ${hasAnalysis ? 'text-brand-purple' : 'text-gray-300'}`}>
              {hasAnalysis ? `${assignment.analysisProgress}%` : '--%'}
            </div>
            <div className="mt-1 flex items-center gap-1 text-[11px] text-brand-purple/60">
              <FlaskConical className="h-3 w-3" /> Analysis
            </div>
          </div>
        </div>

        {/* Analysis progress bar */}
        {hasAnalysis && assignment.analysisProgress > 0 && (
          <div className="mt-3 h-1 overflow-hidden rounded-full bg-gray-100">
            <div
              className="h-full rounded-full bg-brand-purple transition-all"
              style={{ width: `${assignment.analysisProgress}%` }}
            />
          </div>
        )}

        {/* Due date footer */}
        {assignment.dueDate && (
          <div className={`mt-3 flex items-center gap-1.5 border-t border-gray-100 pt-3 text-xs ${
            overdue && !isOpen ? 'text-red-500' : 'text-gray-400'
          }`}>
            {overdue && !isOpen
              ? <AlertTriangle className="h-3 w-3 shrink-0" />
              : <Calendar className="h-3 w-3 shrink-0" />
            }
            <span>{overdue && !isOpen ? 'Closed · ' : 'Due: '}</span>
            <span className="truncate">{formatDueDate(assignment.dueDate)}</span>
          </div>
        )}
      </div>
    </Link>
  )
}


/* ── Assignment List Item (list view) ── */
function AssignmentListItem({ assignment, courseId }) {
  const isOpen    = assignment.isOpen
  const overdue   = isOverdue(assignment.dueDate)
  const langClass = LANG_COLORS[assignment.language?.toLowerCase()] || 'bg-gray-100 text-gray-600'

  return (
    <Link
      to={`/course/${courseId}/assignment/${assignment.id}`}
      className="flex items-center justify-between px-5 py-4 transition-colors hover:bg-brand-purple/[0.025] no-underline group"
    >
      <div className="flex items-center gap-3 min-w-0">
        {/* Status stripe */}
        <div className={`h-9 w-1 shrink-0 rounded-full ${isOpen ? 'bg-brand-purple/50' : 'bg-gray-200'}`} />
        <div className="min-w-0">
          <span className="block truncate text-sm font-semibold text-gray-900 group-hover:text-brand-purple transition-colors">
            {assignment.title}
          </span>
          <div className="mt-1 flex items-center gap-2">
            <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${
              isOpen ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-500'
            }`}>
              {isOpen ? 'Open' : 'Closed'}
            </span>
            {assignment.language && (
              <span className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${langClass}`}>
                {assignment.language.toUpperCase()}
              </span>
            )}
            {assignment.dueDate && (
              <span className={`flex items-center gap-1 text-[11px] ${
                overdue && !isOpen ? 'text-red-500' : 'text-gray-400'
              }`}>
                {overdue && !isOpen
                  ? <AlertTriangle className="h-3 w-3" />
                  : <Clock className="h-3 w-3" />
                }
                {formatDueDate(assignment.dueDate)}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-6 shrink-0 ml-4">
        <div className="text-right">
          <div className="text-sm font-bold text-brand-purple">{assignment.submissionCount ?? 0}</div>
          <div className="text-[11px] text-gray-400">submissions</div>
        </div>
        {assignment.analysisProgress != null && (
          <div className="text-right">
            <div className="text-sm font-bold text-brand-purple">{assignment.analysisProgress}%</div>
            <div className="text-[11px] text-gray-400">analysis</div>
          </div>
        )}
        <ChevronRight className="h-4 w-4 text-gray-300 group-hover:text-brand-purple transition-colors" />
      </div>
    </Link>
  )
}
