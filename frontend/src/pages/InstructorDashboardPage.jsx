import { useState } from 'react'
import AppShell from '../components/AppShell'
import HomePage from './HomePage'
import CoursePage from './CoursePage'
import AssignmentDetailPage from './AssignmentDetailPage'
import SubmissionComparePage from './SubmissionComparePage'

/**
 * InstructorDashboardPage — top-level shell.
 * activePage:
 *   { type: 'home' }
 *   { type: 'course',      courseId, courseName }
 *   { type: 'assignment',  courseId, courseName, assignmentId }
 *   { type: 'compare',     courseId, courseName, assignmentId, submissionId }
 *
 * Props:
 *   onLogout: () => void
 */
export default function InstructorDashboardPage({ onLogout }) {
  const [activePage, setActivePage] = useState({ type: 'home' })
  const [sidebarKey, setSidebarKey] = useState(0)

  function goHome() { setActivePage({ type: 'home' }) }

  function goToCourse(courseId, courseName) {
    setActivePage({ type: 'course', courseId, courseName })
  }

  function goToAssignment(assignmentId, courseId) {
    setActivePage((p) => ({
      type: 'assignment',
      courseId,
      courseName: p.courseId === courseId ? p.courseName : '',
      assignmentId,
    }))
  }

  function goToCompare(submissionId, assignmentId) {
    setActivePage((p) => ({ ...p, type: 'compare', submissionId, assignmentId }))
  }

  function refreshSidebar() { setSidebarKey((k) => k + 1) }

  return (
    <AppShell
      activePage={activePage}
      onGoHome={goHome}
      onSelectCourse={(id) => goToCourse(id, '')}
      onSelectAssignment={goToAssignment}
      onLogout={onLogout}
      refreshKey={sidebarKey}
    >
      {activePage.type === 'home' && (
        <HomePage
          onSelectCourse={(id) => goToCourse(id, '')}
          onCourseCreated={refreshSidebar}
        />
      )}
      {activePage.type === 'course' && (
        <CoursePage
          courseId={activePage.courseId}
          courseName={activePage.courseName}
          onSelectAssignment={goToAssignment}
          onAssignmentCreated={refreshSidebar}
        />
      )}
      {activePage.type === 'assignment' && (
        <AssignmentDetailPage
          assignmentId={activePage.assignmentId}
          onSelectSubmission={goToCompare}
        />
      )}
      {activePage.type === 'compare' && (
        <SubmissionComparePage
          submissionId={activePage.submissionId}
          assignmentId={activePage.assignmentId}
          onBack={() => goToAssignment(activePage.assignmentId, activePage.courseId)}
        />
      )}
    </AppShell>
  )
}
