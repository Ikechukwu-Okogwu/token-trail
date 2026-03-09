import Sidebar from "../components/Sidebar/Sidebar"

/**
 * Stub: Instructor dashboard page.
 * TODO: wire up to GET /api/instructor/courses
 */
export default function InstructorDashboardPage({ courses = [] }) {
  return (
    <div className="h-screen flex">
      <Sidebar courses={courses}></Sidebar>
      <main className="ml-55 flex-1">
        <h2>Instructor Dashboard</h2>
        <p>Course and assignment management will go here.</p>
      </main>
    </div>
  )
}
