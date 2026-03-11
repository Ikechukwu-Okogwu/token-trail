import { useState } from 'react'
import AppShell from '../components/AppShell'
import HomePage from './HomePage'
import CoursePage from './CoursePage'

/**
 * InstructorDashboardPage
 *
 * YOUR SCOPE:
 *   - home  → HomePage (course cards)
 *   - course → CoursePage (assignment cards + Course Settings tab)
 *
 * TEAMMATE'S SCOPE (handed off via onSelectAssignment prop):
 *   - assignment detail page
 *   - submission compare page
 *
 * Props:
 *   onSelectAssignment (assignmentId, courseId) => void  ← inject your teammate's handler here
 *   onLogout           () => void
 */
export default function InstructorDashboardPage({ onSelectAssignment, onLogout }) {
  const [activePage, setActivePage] = useState({ type: 'home' })
  const [sidebarKey, setSidebarKey] = useState(0)

  function goHome() {
    setActivePage({ type: 'home' })
  }

  function goToCourse(courseId, courseName) {
    setActivePage({ type: 'course', courseId, courseName: courseName || '' })
  }

  function refreshSidebar() {
    setSidebarKey((k) => k + 1)
  }

  // When an assignment is clicked (sidebar or card) — hand off to teammate
  function handleSelectAssignment(assignmentId, courseId) {
    onSelectAssignment?.(assignmentId, courseId)
  }

  return (
    <AppShell
      activePage={activePage}
      onGoHome={goHome}
      onSelectCourse={goToCourse}
      onSelectAssignment={handleSelectAssignment}
      onLogout={onLogout}
      refreshKey={sidebarKey}
    >
      {activePage.type === 'home' && (
        <HomePage
          onSelectCourse={goToCourse}
          onCourseCreated={refreshSidebar}
        />
      )}

      {activePage.type === 'course' && (
        <CoursePage
          courseId={activePage.courseId}
          courseName={activePage.courseName}
          onSelectAssignment={handleSelectAssignment}
          onAssignmentCreated={refreshSidebar}
        />
      )}
    </AppShell>
  )
}
