import { useState, useEffect } from 'react'
import { apiFetch } from '../services/api'
import CreateCourseForm from './CreateCourseForm'

/**
 * AppShell — full-height layout: dark sidebar + main content area.
 * Props:
 *   activePage: { type, courseId?, assignmentId?, submissionId? }
 *   onGoHome, onSelectCourse, onSelectAssignment: navigation callbacks
 *   onLogout: () => void
 *   refreshKey: number
 *   children: main content
 */
export default function AppShell({
  activePage,
  onGoHome,
  onSelectCourse,
  onSelectAssignment,
  onLogout,
  refreshKey = 0,
  children,
}) {
  const [courses, setCourses] = useState([])
  const [expandedIds, setExpandedIds] = useState({})
  const [showCreateCourse, setShowCreateCourse] = useState(false)
  const [sidebarRefresh, setSidebarRefresh] = useState(0)

  useEffect(() => {
    apiFetch('/instructor/courses')
      .then((data) => {
        setCourses(data)
        if (activePage?.courseId) {
          setExpandedIds((p) => ({ ...p, [activePage.courseId]: true }))
        }
      })
      .catch(console.error)
  }, [refreshKey, sidebarRefresh])

  function toggle(id) {
    setExpandedIds((p) => ({ ...p, [id]: !p[id] }))
  }

  function handleCourseCreated(course) {
    setShowCreateCourse(false)
    setSidebarRefresh((k) => k + 1)
    onSelectCourse(course.id)
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#f0f0f4] font-sans">

      {/* ── Sidebar ── */}
      <aside className="flex flex-col w-[240px] min-w-[240px] bg-[#3b3660] text-white overflow-hidden">

        {/* Brand */}
        <div className="px-6 pt-6 pb-4 border-b border-white/10">
          <span className="text-2xl font-bold tracking-tight">Token Trail</span>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-3 scrollbar-none">
          {/* Home */}
          <button
            onClick={onGoHome}
            className={`flex items-center gap-3 w-full px-5 py-2.5 text-sm font-medium transition-colors
              ${activePage?.type === 'home'
                ? 'bg-white/20 border-l-2 border-white text-white'
                : 'text-white/70 hover:bg-white/10 hover:text-white'}`}
          >
            {/* Home icon */}
            <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7m-9-5v12a1 1 0 001 1h3m4-13l2 2m-2-2v12a1 1 0 01-1 1h-3m-4 0h4"/>
            </svg>
            Home
          </button>

          {/* Courses */}
          {courses.map((course) => (
            <div key={course.id}>
              <button
                onClick={() => { toggle(course.id); onSelectCourse(course.id) }}
                className={`flex items-center gap-3 w-full px-5 py-2.5 text-sm font-medium transition-colors
                  ${activePage?.courseId === course.id && activePage?.type !== 'home'
                    ? 'bg-white/20 border-l-2 border-white text-white'
                    : 'text-white/70 hover:bg-white/10 hover:text-white'}`}
              >
                {/* Mortarboard icon */}
                <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l9-5-9-5-9 5 9 5z"/>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l6.16-3.422A12.083 12.083 0 0121 12c0 3.314-4.03 6-9 6s-9-2.686-9-6c0-.538.09-1.064.254-1.565L12 14z"/>
                </svg>
                <span className="flex-1 truncate text-left">{course.name}</span>
                {/* Chevron pill */}
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-white/15 text-white/80">
                  <svg className={`w-3 h-3 transition-transform ${expandedIds[course.id] ? 'rotate-180' : ''}`}
                    fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7"/>
                  </svg>
                </span>
              </button>

              {/* Assignments */}
              {expandedIds[course.id] && course.assignments?.map((a) => (
                <button
                  key={a.id}
                  onClick={() => onSelectAssignment(a.id, course.id)}
                  className={`flex items-center gap-3 w-full pl-12 pr-5 py-2 text-sm transition-colors
                    ${activePage?.assignmentId === a.id
                      ? 'bg-white/15 text-white font-medium'
                      : 'text-white/60 hover:bg-white/10 hover:text-white'}`}
                >
                  {/* Document icon */}
                  <svg className="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414A1 1 0 0121 9.414V19a2 2 0 01-2 2z"/>
                  </svg>
                  <span className="truncate">{a.title}</span>
                </button>
              ))}
            </div>
          ))}
        </nav>

        {/* Bottom: profile + bell */}
        <div className="border-t border-white/10 px-6 py-4 flex items-center gap-6">
          <button onClick={onLogout} className="text-white/60 hover:text-white transition-colors" aria-label="Profile / Logout">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </button>
          <button className="text-white/60 hover:text-white transition-colors" aria-label="Notifications">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
          </button>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>

      {/* Create course modal */}
      {showCreateCourse && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md">
            <CreateCourseForm
              onCreated={handleCourseCreated}
              onCancel={() => setShowCreateCourse(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}
