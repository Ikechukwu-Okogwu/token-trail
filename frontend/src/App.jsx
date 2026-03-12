import { useState, useEffect, Fragment } from 'react'
import {Routes, Route} from 'react-router-dom'
import Sidebar from './components/Sidebar/Sidebar'
import LoginPage from './pages/LoginPage'
import InstructorDashboardPage from './pages/InstructorDashboardPage'
import StudentSubmitPage from './pages/StudentSubmitPage'
import AssignmentPage from './pages/AssignmentPage'
import AssignmentDetailPage from './pages/AssignmentDetailPage'
import CoursePage from './pages/CoursePage'
import SubmissionComparisonPage from './pages/SubmissionComparisonPage'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const token = localStorage.getItem("token");

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [courses, setCourses] = useState([])

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((res) => res.json())
      .then((data) => {
        setHealth(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
      
  }, [])

  useEffect(() => { //sample values
    setCourses([
      {id:"1", name:"COSC 4P02", assignments: [
        { id: "a1", title: "Assignment 1", details: true },
        { id: "a2", title: "Assignment 2" },
        { id: "a3", title: "Assignment 3" },
      ],}, 
      {id:"2", name:"COSC 4P01", assignments:[]}])
  }, [])

  if (loading) return <p>Loading...</p>
  if (error) return <p>Error: {error}</p>

  return (
    <div>
      {/* <h1>Token Trail</h1>
      <p>Health check from backend:</p>
      <pre style={{ background: '#16213e', padding: '1rem', borderRadius: 8 }}>
        {JSON.stringify(health, null, 2)}
      </pre> */}
      <Routes>
        <Route path="/" element={<LoginPage/>}/>
        <Route path="/dashboard" element={<InstructorDashboardPage courses={courses}/>}/>
        <Route path="/student-submit" element={<StudentSubmitPage/>}/>
        <Route path="/course/:courseId/assignment/:assignmentId/submission/:submissionId" element={<SubmissionComparisonPage courses={courses}/>}/>
        {courses.map((course) => (
          <Fragment key={course.id}>
            <Route path={`/course/${course.id}`} element={<CoursePage courses={courses}/>}/>
            {course.assignments.map((assignment) => (
              <Fragment key={assignment.id}>
                <Route path={`/course/${course.id}/assignment/${assignment.id}`} element={<AssignmentPage courses={courses}/>}/>
                {assignment.details && (
                  <Route path={`/course/${course.id}/assignment/${assignment.id}/details`} element={<AssignmentDetailPage/>}/>
                )}
              </Fragment>
            ))}
          </Fragment>
        ))}
      </Routes>
      
    </div>
  )
}

export default App
