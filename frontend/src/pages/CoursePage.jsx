import { useState, useEffect } from 'react'
import { apiFetch } from '../services/api'
import CreateAssignmentForm from '../components/CreateAssignmentForm'

/**
 * CoursePage — shows a course's assignments in a grid.
 * Header: "COSC 4P02 ⚙" + toolbar + cards
 * Props:
 *   courseId: string
 *   courseName: string
 *   onSelectAssignment: (assignmentId, courseId) => void
 *   onAssignmentCreated: () => void
 */
export default function CoursePage({ courseId, courseName, onSelectAssignment, onAssignmentCreated }) {
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [viewMode, setViewMode] = useState('grid')
  const [showCreate, setShowCreate] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    setLoading(true)
    apiFetch('/instructor/courses')
      .then((courses) => {
        const course = courses.find((c) => c.id === courseId)
        setAssignments(course?.assignments || [])
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [courseId, refreshKey])

  function handleCreated(assignment) {
    setShowCreate(false)
    setRefreshKey((k) => k + 1)
    onAssignmentCreated?.()
    onSelectAssignment(assignment.id, courseId)
  }

  const filtered = assignments.filter((a) =>
    a.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="p-6 min-h-full">
      <div className="bg-white rounded-2xl shadow-sm p-6 min-h-full">

        {/* Page header */}
        <div className="flex items-center gap-2 mb-5">
          <h1 className="text-xl font-bold text-gray-900">{courseName ?? 'Course'}</h1>
          <button className="text-gray-400 hover:text-gray-700 transition-colors" aria-label="Course settings">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
        </div>

        {/* Toolbar */}
        <div className="flex items-center gap-3 mb-6">
          <div className="flex-1 flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-2.5">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h7"/>
            </svg>
            <input
              type="text" placeholder="Hinted search text" value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 bg-transparent text-sm text-gray-600 placeholder-gray-400 outline-none"
            />
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </div>

          <div className="flex items-center bg-gray-100 rounded-xl p-1">
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-white shadow-sm text-gray-800' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-white shadow-sm text-gray-800' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
                <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
              </svg>
            </button>
          </div>

          <div className="w-px h-8 bg-gray-200"/>

          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 bg-[#3b3660] text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-[#2d2b4a] transition-colors shadow-sm"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
            New
          </button>
        </div>

        {/* Cards */}
        {loading ? (
          <div className="text-gray-400 text-sm text-center py-12">Loading assignments…</div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-3 gap-4' : 'flex flex-col gap-3'}>
            {filtered.map((a) => (
              <AssignmentCard
                key={a.id}
                assignment={a}
                onSelect={() => onSelectAssignment(a.id, courseId)}
              />
            ))}
          </div>
        )}
      </div>

      {showCreate && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md">
            <CreateAssignmentForm courseId={courseId} onCreated={handleCreated} onCancel={() => setShowCreate(false)} />
          </div>
        </div>
      )}
    </div>
  )
}

function AssignmentCard({ assignment, onSelect }) {
  const isOpen = assignment.isOpen
  return (
    <div
      onClick={onSelect}
      className="relative bg-white border border-gray-200 rounded-2xl p-5 cursor-pointer hover:shadow-md hover:border-gray-300 transition-all group"
    >
      {/* Open/Closed badge */}
      <div className={`absolute top-3 left-4 text-xs font-semibold ${isOpen ? 'text-green-500' : 'text-red-400'}`}>
        {isOpen ? 'Open' : 'Closed'}
      </div>

      <div className="flex items-start justify-between mt-4 mb-2">
        <span className="text-base font-bold text-gray-900">{assignment.title}</span>
        <button
          onClick={(e) => e.stopPropagation()}
          className="text-gray-400 hover:text-gray-700 text-lg leading-none px-1"
          aria-label="Options"
        >⋮</button>
      </div>
      <hr className="border-gray-100 mb-4"/>

      <div className="flex gap-6 mb-4">
        <div>
          <div className="text-3xl font-bold text-gray-900">{assignment.submissionCount ?? '--'}</div>
          <div className="text-xs text-gray-500 mt-0.5">Submissions</div>
        </div>
        <div>
          <div className="text-3xl font-bold text-gray-400">
            {assignment.analysisProgress != null ? `${assignment.analysisProgress}%` : '--%'}
          </div>
          <div className="text-xs text-gray-500 mt-0.5">Analysis Progress</div>
        </div>
      </div>

      {assignment.dueDate && (
        <div className="text-xs text-gray-400 text-center pt-2 border-t border-gray-100">
          Due Date: {assignment.dueDate}
        </div>
      )}
    </div>
  )
}
