import { useState, useEffect, useRef } from 'react'
import { NavLink, useLocation, useParams } from 'react-router-dom'
import './Sidebar.css'
import homeIcon from '../../assets/icons/home.svg'
import courseIcon from '../../assets/icons/course.svg'
import accountIcon from '../../assets/icons/account.svg'
import notificationsIcon from '../../assets/icons/notifications.svg'
import assignmentIcon from '../../assets/icons/assignment.svg'
import { getCourseAssignments, getInstructorCourses, getAnalysisRunStatus, logout } from '../../services/api'

function Chevron({ open }) {
  return (
    <svg
      className={`w-3 h-3 transition-transform duration-200 ease-in-out ${open ? 'rotate-180' : 'rotate-0'}`}
      viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
      strokeLinecap="round" strokeLinejoin="round"
    >
      <path d="M6 9l6 6 6-6" />
    </svg>
  )
}

export default function Sidebar({ refreshKey }) {
  const location = useLocation()
  const [courses, setCourses] = useState([])
  const token = localStorage.getItem('token')
  const [acctMenuOpen, setAcctMenuOpen] = useState(false)
  const acctMenuRef = useRef(null)
  const acctBtnRef = useRef(null)
  const [courseAssignments, setCourseAssignments] = useState({})
  const [loadingCourseAssignments, setLoadingCourseAssignments] = useState({})
  const [expandedIds, setExpandedIds] = useState(new Set())
  const { runId } = useParams()
  const [runStatus, setRunStatus] = useState(null)

  const fetchAssignments = (courseId) => {
    if (courseAssignments[courseId] || loadingCourseAssignments[courseId]) return
    setLoadingCourseAssignments((prev) => ({ ...prev, [courseId]: true }))
    getCourseAssignments(courseId)
      .then((data) => setCourseAssignments((prev) => ({ ...prev, [courseId]: Array.isArray(data) ? data : [] })))
      .catch(() => setCourseAssignments((prev) => ({ ...prev, [courseId]: [] })))
      .finally(() => setLoadingCourseAssignments((prev) => ({ ...prev, [courseId]: false })))
  }

  useEffect(() => {
    if (token) {
      getInstructorCourses()
        .then(setCourses)
        .catch((err) => console.error('Failed to fetch courses:', err))
    }
  }, [token, refreshKey])

  useEffect(() => {
    if (runId) {
      getAnalysisRunStatus(runId)
        .then(setRunStatus)
        .catch(console.error)
    }
  }, [runId])

  useEffect(() => {
    if (!runStatus || courses.length === 0) return
    setExpandedIds(prev => { const next = new Set(prev); next.add(runStatus.courseId); return next })
  }, [runStatus, courses])

  useEffect(() => {
    if (runStatus) return
    setExpandedIds(prev => {
      const next = new Set(prev)
      courses.forEach(course => {
        if (location.pathname.startsWith(`/course/${course.id}`)) next.add(course.id)
      })
      return next
    })
  }, [courses, location.pathname, runStatus])

  useEffect(() => {
    if (!runStatus || courses.length === 0) return
    const courseId = runStatus.courseId
    if (!courseAssignments[courseId] && !loadingCourseAssignments[courseId]) fetchAssignments(courseId)
  }, [runStatus, courses, courseAssignments, loadingCourseAssignments])

  useEffect(() => {
    const match = location.pathname.match(/^\/course\/([^/]+)(?:\/assignment\/[^/]+)?$/)
    if (match) {
      const courseId = match[1]
      if (!courseAssignments[courseId] && !loadingCourseAssignments[courseId]) fetchAssignments(courseId)
    }
  }, [location.pathname, courseAssignments, loadingCourseAssignments])

  useEffect(() => {
    function handleClickOutside(e) {
      if (
        acctMenuRef.current && !acctMenuRef.current.contains(e.target) &&
        acctBtnRef.current && !acctBtnRef.current.contains(e.target)
      ) {
        setAcctMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const toggleCourse = (courseId) => {
    const isCurrentlyExpanded = expandedIds.has(courseId)
    setExpandedIds((prev) => {
      const next = new Set(prev)
      next.has(courseId) ? next.delete(courseId) : next.add(courseId)
      return next
    })
    if (!isCurrentlyExpanded) fetchAssignments(courseId)
  }

  return (
    <aside
      className="fixed top-0 left-0 h-screen w-55 text-brand-pink shadow-right-sidebar shrink-0 flex flex-col"
      style={{
        fontFamily: "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
        background: 'linear-gradient(175deg, #4a4360 0%, #524b63 40%, #564F67 100%)',
      }}
    >

      {/* ── Logo ── */}
      <a
        href="/dashboard"
        className="flex items-center gap-2.5 px-4 pt-5 pb-4 no-underline group"
      >
        {/* Brand mark */}
        <div className="h-6 w-6 rounded-[6px] bg-brand-pink/15 flex items-center justify-center flex-shrink-0 ring-1 ring-brand-pink/20 group-hover:bg-brand-pink/20 transition-colors duration-150">
          <svg className="w-3.5 h-3.5 text-brand-pink/80" viewBox="0 0 16 16" fill="none">
            <circle cx="5" cy="5" r="2.5" fill="currentColor" opacity="0.9"/>
            <circle cx="11" cy="5" r="2.5" fill="currentColor" opacity="0.5"/>
            <circle cx="5" cy="11" r="2.5" fill="currentColor" opacity="0.5"/>
            <circle cx="11" cy="11" r="2.5" fill="currentColor" opacity="0.25"/>
          </svg>
        </div>
        {/* Word mark */}
        <span
          className="text-brand-pink font-semibold tracking-[-0.02em] leading-none"
          style={{ fontSize: '1.05rem' }}
        >
          Token Trail
        </span>
      </a>

      {/* ── Navigation ── */}
      <div className="grow overflow-y-auto px-2 pb-4" style={{ scrollbarWidth: 'none' }}>

        {/* Home */}
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `relative flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] transition-all duration-150 ease-in-out ${
              isActive
                ? 'bg-white/[0.13] text-brand-pink font-medium shadow-[inset_0_1px_0_rgba(255,255,255,0.07)]'
                : 'text-brand-pink/65 font-normal hover:bg-white/[0.07] hover:text-brand-pink/90'
            }`
          }
        >
          {({ isActive }) => (
            <>
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 h-[18px] w-[3px] rounded-r-full bg-brand-pink/90 shadow-[0_0_6px_rgba(254,247,255,0.4)]" />
              )}
              <img src={homeIcon} alt="" className="w-4 h-4 shrink-0 opacity-70" />
              <span>Home</span>
            </>
          )}
        </NavLink>

        {/* Courses section label */}
        {courses.length > 0 && (
          <div className="mt-5 mb-1.5 px-3">
            <span
              className="text-brand-pink/30 font-semibold uppercase"
              style={{ fontSize: '10px', letterSpacing: '0.08em' }}
            >
              Courses
            </span>
          </div>
        )}

        {/* Course list */}
        <div className="flex flex-col gap-px">
          {courses.map((course) => {
            const assignments = courseAssignments[course.id] ?? []
            const isExpanded = expandedIds.has(course.id)
            const isExactCourse = location.pathname === `/course/${course.id}`

            return (
              <div key={course.id}>
                {/* Course row */}
                <div className="flex items-center gap-0.5">
                  <NavLink
                    to={`/course/${course.id}`}
                    className={({ isActive }) => {
                      const active = isActive && isExactCourse
                      return `relative flex items-center gap-2.5 flex-1 min-w-0 rounded-lg py-2 pl-3 pr-1 text-[13px] transition-all duration-150 ease-in-out ${
                        active
                          ? 'bg-white/[0.13] text-brand-pink font-medium shadow-[inset_0_1px_0_rgba(255,255,255,0.07)]'
                          : 'text-brand-pink/65 font-normal hover:bg-white/[0.07] hover:text-brand-pink/90'
                      }`
                    }}
                  >
                    {({ isActive }) => {
                      const active = isActive && isExactCourse
                      return (
                        <>
                          {active && (
                            <span className="absolute left-0 top-1/2 -translate-y-1/2 h-[18px] w-[3px] rounded-r-full bg-brand-pink/90 shadow-[0_0_6px_rgba(254,247,255,0.4)]" />
                          )}
                          <img src={courseIcon} alt="" className="w-4 h-4 shrink-0 opacity-65" />
                          <div className="min-w-0 flex-1">
                            <div className="truncate leading-tight">{course.name}</div>
                            {course.term && (
                              <div
                                className="text-brand-pink/35 leading-tight mt-0.5 truncate"
                                style={{ fontSize: '11px' }}
                              >
                                {course.term}
                              </div>
                            )}
                          </div>
                        </>
                      )
                    }}
                  </NavLink>

                  <button
                    onClick={() => toggleCourse(course.id)}
                    className="flex-shrink-0 p-1.5 rounded-md text-brand-pink/35 hover:text-brand-pink/70 hover:bg-white/[0.07] transition-all duration-150 ease-in-out cursor-pointer"
                    aria-expanded={isExpanded}
                  >
                    <Chevron open={isExpanded} />
                  </button>
                </div>

                {/* Assignment list */}
                {isExpanded && (
                  <div className="mt-px mb-1 ml-[1.05rem] pl-3.5 border-l border-white/[0.10] flex flex-col gap-px">
                    {loadingCourseAssignments[course.id] ? (
                      <div className="py-2 px-2 text-brand-pink/30" style={{ fontSize: '11px' }}>Loading…</div>
                    ) : assignments.length > 0 ? (
                      assignments.map((a) => {
                        const assignmentActive = a.id === runStatus?.assignmentId
                        return (
                          <NavLink
                            key={a.id}
                            to={`/course/${course.id}/assignment/${a.id}`}
                            className={({ isActive }) => {
                              const active = isActive || assignmentActive
                              return `relative flex items-center gap-2 rounded-md px-2 py-1.5 transition-all duration-150 ease-in-out ${
                                active
                                  ? 'bg-white/[0.10] text-brand-pink font-medium shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]'
                                  : 'text-brand-pink/50 font-normal hover:bg-white/[0.06] hover:text-brand-pink/80'
                              }`
                            }}
                            style={{ fontSize: '12px' }}
                          >
                            {({ isActive }) => {
                              const active = isActive || assignmentActive
                              return (
                                <>
                                  {active && (
                                    <span className="absolute left-0 top-1/2 -translate-y-1/2 h-3.5 w-[2.5px] rounded-r-full bg-brand-pink/75 shadow-[0_0_4px_rgba(254,247,255,0.3)]" />
                                  )}
                                  <img src={assignmentIcon} alt="" className="w-3.5 h-3.5 shrink-0 opacity-50" />
                                  <span className="truncate leading-snug">{a.title}</span>
                                </>
                              )
                            }}
                          </NavLink>
                        )
                      })
                    ) : (
                      <div className="py-2 px-2 text-brand-pink/28 italic" style={{ fontSize: '11px' }}>
                        No assignments yet
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Account popup ── */}
      {acctMenuOpen && (
        <div
          className="absolute bottom-[4.25rem] left-2 w-40 rounded-xl overflow-hidden z-50 border border-white/[0.12] shadow-[0_8px_32px_rgba(0,0,0,0.35)] backdrop-blur-sm"
          style={{ background: 'rgba(58,52,74,0.97)' }}
          ref={acctMenuRef}
        >
          <button className="w-full text-left px-4 py-2.5 text-brand-pink/80 hover:bg-white/[0.08] hover:text-brand-pink transition-colors duration-100"
            style={{ fontSize: '13px' }}>
            Settings
          </button>
          <div className="border-t border-white/[0.10]" />
          <button
            className="w-full text-left px-4 py-2.5 text-red-400/80 hover:bg-red-500/[0.12] hover:text-red-400 transition-colors duration-100"
            style={{ fontSize: '13px' }}
            onClick={() => logout()}
          >
            Sign Out
          </button>
        </div>
      )}

      {/* ── Footer ── */}
      <div className="flex-shrink-0 border-t border-white/[0.08] px-2 py-2">
        <div className="flex items-center gap-1">

          {/* Account button */}
          <button
            className="flex flex-1 items-center gap-2.5 rounded-lg px-2.5 py-2 text-brand-pink/50 transition-all duration-150 ease-in-out hover:bg-white/[0.08] hover:text-brand-pink/85 group cursor-pointer"
            onClick={() => setAcctMenuOpen(prev => !prev)}
            ref={acctBtnRef}
            title="Account"
          >
            <div className="h-6 w-6 rounded-full bg-white/[0.12] flex items-center justify-center flex-shrink-0 ring-1 ring-white/[0.10] group-hover:bg-white/[0.18] group-hover:ring-white/[0.15] transition-all duration-150">
              <img src={accountIcon} alt="" className="h-3.5 w-3.5 opacity-75" />
            </div>
            <span className="text-brand-pink/55 font-medium group-hover:text-brand-pink/80 transition-colors duration-150"
              style={{ fontSize: '12px' }}>
              Account
            </span>
          </button>

          {/* Divider */}
          <div className="h-5 w-px bg-white/[0.08] flex-shrink-0" />

          {/* Notifications button */}
          <button
            className="flex items-center justify-center rounded-lg p-2 text-brand-pink/50 transition-all duration-150 ease-in-out hover:bg-white/[0.08] hover:text-brand-pink/85 cursor-pointer"
            title="Notifications"
          >
            <img src={notificationsIcon} alt="Notifications" className="h-4 w-4 opacity-70" />
          </button>

        </div>
      </div>
    </aside>
  )
}
