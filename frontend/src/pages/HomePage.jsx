import { useState, useEffect } from 'react'
import { apiFetch } from '../services/api'
import CreateCourseForm from '../components/CreateCourseForm'

/**
 * HomePage — instructor home, shows all courses as cards.
 * Props:
 *   onSelectCourse: (courseId) => void
 *   onCourseCreated: () => void  — tells shell to refetch sidebar
 */
export default function HomePage({ onSelectCourse, onCourseCreated }) {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [viewMode, setViewMode] = useState('grid')
  const [showCreate, setShowCreate] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    setLoading(true)
    apiFetch('/instructor/courses')
      .then(setCourses)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [refreshKey])

  function handleCreated(course) {
    setShowCreate(false)
    setRefreshKey((k) => k + 1)
    onCourseCreated?.()
    onSelectCourse(course.id)
  }

  const filtered = courses.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="p-6 min-h-full">
      <div className="bg-white rounded-2xl shadow-sm p-6 min-h-full">

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

          {/* View toggle */}
          <div className="flex items-center bg-gray-100 rounded-xl p-1">
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-white shadow-sm text-gray-800' : 'text-gray-400 hover:text-gray-600'}`}
              aria-label="List view"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-white shadow-sm text-gray-800' : 'text-gray-400 hover:text-gray-600'}`}
              aria-label="Grid view"
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

        {/* Grid */}
        {loading ? (
          <div className="text-gray-400 text-sm text-center py-12">Loading courses…</div>
        ) : (
          <div className={viewMode === 'grid'
            ? 'grid grid-cols-3 gap-4'
            : 'flex flex-col gap-3'}>
            {filtered.map((course) => (
              <CourseCard key={course.id} course={course} onSelect={onSelectCourse} />
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md">
            <CreateCourseForm onCreated={handleCreated} onCancel={() => setShowCreate(false)} />
          </div>
        </div>
      )}
    </div>
  )
}

function CourseCard({ course, onSelect }) {
  return (
    <div
      onClick={() => onSelect(course.id)}
      className="bg-white border border-gray-200 rounded-2xl p-5 cursor-pointer hover:shadow-md hover:border-gray-300 transition-all group"
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-base font-bold text-gray-900">{course.name}</span>
        <button
          onClick={(e) => e.stopPropagation()}
          className="text-gray-400 hover:text-gray-700 text-lg leading-none px-1 opacity-0 group-hover:opacity-100 transition-opacity"
          aria-label="Options"
        >⋮</button>
      </div>
      <hr className="border-gray-100 mb-4"/>
      <div className="flex gap-6">
        <div>
          <div className="text-3xl font-bold text-gray-900">{course.assignmentCount ?? 0}</div>
          <div className="text-xs text-gray-500 mt-0.5">Assignments</div>
        </div>
        <div>
          <div className="text-3xl font-bold text-gray-900">{course.analysisCompleteCount ?? 0}</div>
          <div className="text-xs text-gray-500 mt-0.5">Analyses Complete</div>
        </div>
      </div>
    </div>
  )
}
