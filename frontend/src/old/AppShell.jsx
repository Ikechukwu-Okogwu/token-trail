import { useState, useEffect } from 'react'
import { apiFetch } from '../services/api'
import CreateCourseForm from './CreateCourseForm'

/**
 * AppShell — sidebar layout shell.
 *
 * Props:
 *   activePage        { type: 'home' } | { type: 'course', courseId, courseName }
 *   onGoHome          () => void
 *   onSelectCourse    (courseId, courseName) => void
 *   onSelectAssignment (assignmentId, courseId) => void   ← passed to teammate's page
 *   onLogout          () => void
 *   refreshKey        number — increment to force sidebar refetch
 *   children          main content area
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

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#f0f0f4]">

      {/* ══ Sidebar ══ */}
      <aside className="flex flex-col w-[240px] min-w-[240px] bg-[#3b3660] text-white overflow-hidden">

        {/* Brand */}
        <div className="px-6 pt-5 pb-4 border-b border-white/10 flex-shrink-0">
          <span className="text-xl font-bold tracking-tight select-none">Token Trail</span>
        </div>

        {/* Nav list */}
        <nav className="flex-1 overflow-y-auto py-2" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>

          {/* ── Home ── */}
          <button
            onClick={onGoHome}
            className={[
              'w-full flex items-center gap-3 px-5 py-2.5 text-sm font-medium transition-colors text-left',
              activePage?.type === 'home'
                ? 'bg-white/20 text-white border-l-[3px] border-white pl-[17px]'
                : 'text-white/70 hover:bg-white/10 hover:text-white',
            ].join(' ')}
          >
            {/* House icon — display:block prevents inline baseline gap */}
            <svg style={{ display: 'block', flexShrink: 0, width: 16, height: 16 }}
              fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
            <span style={{ lineHeight: 1 }}>Home</span>
          </button>

          {/* ── Courses ── */}
          {courses.map((course) => {
            const isCourseActive = activePage?.courseId === course.id
            const isExpanded = !!expandedIds[course.id]

            return (
              <div key={course.id}>
                <button
                  onClick={() => { toggle(course.id); onSelectCourse(course.id, course.name) }}
                  className={[
                    'w-full flex items-center gap-3 px-5 py-2.5 text-sm font-medium transition-colors text-left',
                    isCourseActive
                      ? 'bg-white/20 text-white border-l-[3px] border-white pl-[17px]'
                      : 'text-white/70 hover:bg-white/10 hover:text-white',
                  ].join(' ')}
                >
                  {/* Mortarboard icon */}
                  <svg style={{ display: 'block', flexShrink: 0, width: 16, height: 16 }}
                    fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M12 14l9-5-9-5-9 5 9 5z"/>
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M12 14l6.16-3.422A12.083 12.083 0 0121 12c0 3.314-4.03 6-9 6s-9-2.686-9-6c0-.538.09-1.064.254-1.565L12 14z"/>
                  </svg>
                  <span style={{ lineHeight: 1, flex: 1 }} className="truncate">{course.name}</span>
                  {/* Chevron pill */}
                  <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center',
                    width: 24, height: 24, borderRadius: '50%', background: 'rgba(255,255,255,0.15)',
                    flexShrink: 0 }}>
                    <svg style={{ display: 'block', width: 12, height: 12,
                      transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.2s' }}
                      fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7"/>
                    </svg>
                  </span>
                </button>

                {/* Assignment sub-items */}
                {isExpanded && course.assignments?.map((a) => (
                  <button
                    key={a.id}
                    onClick={() => onSelectAssignment?.(a.id, course.id)}
                    className={[
                      'w-full flex items-center gap-2.5 pl-11 pr-4 py-2 text-sm transition-colors text-left',
                      activePage?.assignmentId === a.id
                        ? 'bg-white/15 text-white font-medium'
                        : 'text-white/55 hover:bg-white/10 hover:text-white',
                    ].join(' ')}
                  >
                    <svg style={{ display: 'block', flexShrink: 0, width: 14, height: 14 }}
                      fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414A1 1 0 0121 9.414V19a2 2 0 01-2 2z"/>
                    </svg>
                    <span style={{ lineHeight: 1 }} className="truncate">{a.title}</span>
                  </button>
                ))}
              </div>
            )
          })}
        </nav>

        {/* Bottom icons */}
        <div className="border-t border-white/10 px-6 py-4 flex items-center gap-5 flex-shrink-0">
          <button onClick={onLogout} className="text-white/60 hover:text-white transition-colors" aria-label="Profile">
            <svg style={{ display: 'block', width: 24, height: 24 }}
              fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </button>
          <button className="text-white/60 hover:text-white transition-colors" aria-label="Notifications">
            <svg style={{ display: 'block', width: 24, height: 24 }}
              fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
          </button>
        </div>
      </aside>

      {/* ══ Main ══ */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}
