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

  useEffect(() => {
    if (token) {
      setCoursesLoading(true)
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
    // TEMP: sample data for verifying routes/UI
    setCourses([
      {
        id: 'course-1',
        name: 'COSC 4P02',
        assignments: [
          { id: 'a1', title: 'Assignment 1' },
          { id: 'a2', title: 'Assignment 2' },
        ],
      },
      {
        id: 'course-2',
        name: 'COSC 4P01',
        assignments: [{ id: 'a1', title: 'Assignment 1' }],
      },
    ])
  }, [])
  const [expandedIds, setExpandedIds] = useState(new Set())
  useEffect(() => {
    const initial = new Set()

    courses.forEach((course) => {
      const assignments = course.assignments ?? []
      const hasActiveAssignment = assignments.some(
        (a) => location.pathname === `/course/${course.id}/assignment/${a.id}`
      )

      if (hasActiveAssignment) {
        initial.add(course.id)
      }
    })

    setExpandedIds(initial)
  }, [courses, location.pathname])

  const [courseAssignments, setCourseAssignments] = useState({})

  const toggleCourse = async (courseId) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(courseId)) {
        next.delete(courseId)
      } else {
        next.add(courseId)
        // Fetch assignments if not already fetched
        if (!courseAssignments[courseId]) {
          getCourseAssignments(courseId)
            .then((assignments) => {
              setCourseAssignments(prev => ({ ...prev, [courseId]: assignments }))
            })
            .catch((err) => {
              console.error('Failed to fetch assignments for course', courseId, err)
            })
        }
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
              const assignments = courseAssignments[course.id] ?? course.assignments ?? []
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
                  {assignments.length > 0 && (
                    <button 
                      onClick={() => toggleCourse(course.id)} 
                      className="p-1.5 mr-2 flex-0 items-center rounded-[60px] hover:bg-[#FEF7FFBF] text-[#FEF7FFBF] hover:text-brand-purple cursor-pointer"
                      aria-expanded={isExpanded}
                    >
                      <span className="">
                        {isExpanded ? <ChevronUp /> : <ChevronDown />}
                      </span>
                    </button>
                  )}
                  
                </div>
                
                {isExpanded && assignments.length > 0 && (
                  <ul className="border-l-[1.5px] border-purple-clicked ml-5">
                    {assignments.map((a) => (
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
                    ))}
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