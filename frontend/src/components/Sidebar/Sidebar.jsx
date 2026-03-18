import { useState, useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import './Sidebar.css'
import homeIcon from '../../assets/icons/home.svg'
import courseIcon from '../../assets/icons/course.svg'
import accountIcon from '../../assets/icons/account.svg'
import notificationsIcon from '../../assets/icons/notifications.svg'
import assignmentIcon from '../../assets/icons/assignment.svg'
import { getCourseAssignments, getInstructorCourses } from '../../services/api'

const navLinkClass = ({ isActive }) =>
  `flex items-center flex-1 gap-2 h-11 ${isActive ? 'bg-purple-clicked' : 'hover:bg-white/5'}`

const navLinkContent = (isActive, icon, label) => (
  <>
    <div className={`w-2 h-full ${isActive ? 'bg-[#FEF7FFBF]' : ''}`} />
    <img src={icon} alt="" />
    <span className='truncate'>{label}</span>
  </>
)

function ChevronDown({ className = 'w-4 h-4' }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 9l6 6 6-6" />
    </svg>
  )
}

function ChevronUp({ className = 'w-4 h-4' }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 15l-6-6-6 6" />
    </svg>
  )
}

export default function Sidebar({refreshKey}) {
  const location = useLocation()
  const [courses, setCourses] = useState([])
  const token = localStorage.getItem('token')
  const [courseAssignments, setCourseAssignments] = useState({})
  const [loadingCourseAssignments, setLoadingCourseAssignments] = useState({})
  const [expandedIds, setExpandedIds] = useState(new Set())

  const fetchAssignments = (courseId) => {
    if (courseAssignments[courseId] || loadingCourseAssignments[courseId]) return

    setLoadingCourseAssignments((prev) => ({ ...prev, [courseId]: true }))

    getCourseAssignments(courseId)
      .then((data) => {
        setCourseAssignments((prev) => ({
          ...prev,
          [courseId]: Array.isArray(data) ? data : [],
        }))
      })
      .catch((err) => {
        console.error('Failed to fetch assignments for course', courseId, err)
        setCourseAssignments((prev) => ({ ...prev, [courseId]: [] }))
      })
      .finally(() => {
        setLoadingCourseAssignments((prev) => ({ ...prev, [courseId]: false }))
      })
  }

  useEffect(() => {
    if (token) {
      getInstructorCourses()
        .then((fetchedCourses) => {
          setCourses(fetchedCourses)
        })
        .catch((err) => {
          console.error('Failed to fetch courses:', err)
        })
    }
  }, [token, refreshKey])
  
  useEffect(() => {
    setExpandedIds((prevExpanded) => {
      const nextExpanded = new Set(prevExpanded)

      courses.forEach((course) => {
        const isActiveCourse = location.pathname === `/course/${course.id}`
        const isActiveAssignment = location.pathname.startsWith(`/course/${course.id}/assignment/`)

        if (isActiveCourse || isActiveAssignment) {
          nextExpanded.add(course.id)
        }

        const assignments = courseAssignments[course.id] ?? []
        const hasActiveAssignment = assignments.some(
          (a) => location.pathname === `/course/${course.id}/assignment/${a.id}`
        )

        if (hasActiveAssignment) {
          nextExpanded.add(course.id)
        }
      })

      return nextExpanded
    })
  }, [courses, courseAssignments, location.pathname])

  useEffect(() => {
    const match = location.pathname.match(/^\/course\/([^\/]+)(?:\/assignment\/[^\/]+)?$/)
    if (!match) return

    const courseId = match[1]
    if (!courseAssignments[courseId] && !loadingCourseAssignments[courseId]) {
      fetchAssignments(courseId)
    }
  }, [location.pathname, courseAssignments, loadingCourseAssignments])

  const toggleCourse = (courseId) => {
    const isCurrentlyExpanded = expandedIds.has(courseId)

    if (!isCurrentlyExpanded) {
          fetchAssignments(courseId)
    }

    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(courseId)) {
        next.delete(courseId)
      } else {
        next.add(courseId)
      }
      return next
    })

    
  }

  return (
    <aside className="fixed top-0 left-0 h-screen w-55 bg-brand-purple text-brand-pink shadow-right-sidebar shrink-0 flex flex-col">
      <a href="/dashboard" className="font-title title pl-4 py-1" style={{ fontSize: '1.65rem' }}>Token Trail</a>
      <div className="grow overflow-y-auto">
        <nav>
          <ul>
            <li>
              <NavLink to="/dashboard" className={navLinkClass}>
                {({ isActive }) => navLinkContent(isActive, homeIcon, 'Home')}
              </NavLink>
            </li>
            {courses.map((course) => {
              const assignments = courseAssignments[course.id] ?? []
              const isExpanded = expandedIds.has(course.id)
              return (
              <li key={course.id}>
                <div className={`flex items-center ${(location.pathname === `/course/${course.id}`) ? 'bg-purple-clicked' : ''}`}>
                  <NavLink
                    to={`/course/${course.id}`}
                    className={({isActive}) => `flex items-center flex-1 gap-2 h-11 ${(isActive&&location.pathname === `/course/${course.id}`) ? '' : 'hover:bg-white/5'}`}
                  >
                    {({ isActive }) => navLinkContent((isActive&&location.pathname === `/course/${course.id}`), courseIcon, course.name)}
                  </NavLink>
                  <button 
                    onClick={() => toggleCourse(course.id)} 
                    className="p-1.5 mr-2 flex-0 items-center rounded-[60px] hover:bg-[#FEF7FFBF] text-[#FEF7FFBF] hover:text-brand-purple cursor-pointer"
                    aria-expanded={isExpanded}
                  >
                    <span className="">
                      {isExpanded ? <ChevronUp /> : <ChevronDown />}
                    </span>
                  </button>
                </div>
                
                {isExpanded && (
                  <ul className="border-l-[1.5px] border-purple-clicked ml-5">
                    {loadingCourseAssignments[course.id] ? (
                      <li className="text-sm text-[#FEF7FFBF] py-2">Loading assignments…</li>
                    ) : assignments.length > 0 ? (
                      assignments.map((a) => (
                        <li key={a.id}>
                          <NavLink
                            to={`/course/${course.id}/assignment/${a.id}`}
                            className={({ isActive }) => `flex items-center gap-2 h-9 ${isActive ? 'bg-purple-clicked' : 'hover:bg-white/5'}`}
                          >
                            {({ isActive }) => (
                              <>
                                <div className={`w-2 h-full ml-[-1.5px] ${isActive ? 'bg-[#FEF7FFBF]' : ''}`} />
                                <img src={assignmentIcon} alt="" className="w-5 h-5 shrink-0" />
                                <span className="truncate">{a.title}</span>
                              </>
                            )}
                          </NavLink>
                        </li>
                      ))
                    ) : (
                      <li className="text-sm text-[#FEF7FFBF] p-2">No assignments yet</li>
                    )}
                  </ul>
                )}
              </li>
              )
            })}
          </ul>
        </nav>
      </div>
      <div className="h-14 border-t border-t-[#FFFFFF80] flex">
        <button className="flex-1 shadow-button flex items-center justify-center cursor-pointer hover:bg-white/5 ">
          <img src={accountIcon} alt="Account" className='h-8'/>
        </button>
        <button className="flex-1 shadow-button flex items-center justify-center cursor-pointer hover:bg-white/5">
          <img src={notificationsIcon} alt="Notifications" className='h-7'/>
        </button>
      </div>
    </aside>
    )
}