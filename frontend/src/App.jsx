import { useState, useEffect, Fragment } from 'react'
import {Routes, Route} from 'react-router-dom'
import Sidebar from './components/Sidebar/Sidebar'
import LoginPage from './pages/LoginPage'
import InstructorDashboardPage from './pages/InstructorDashboardPage'
import StudentSubmitPage from './pages/StudentSubmitPage'
import AssignmentDetailPage from './pages/AssignmentDetailPage'
import CoursePage from './pages/CoursePage'
import { getInstructorCourses } from './services/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const token = localStorage.getItem("token");

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [courses, setCourses] = useState([])
  const [coursesLoading, setCoursesLoading] = useState(false)

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

  // useEffect(() => {
  //   if (token) {
  //     setCoursesLoading(true)
  //     getInstructorCourses()
  //       .then((fetchedCourses) => {
  //         setCourses(fetchedCourses)
  //         setCoursesLoading(false)
  //       })
  //       .catch((err) => {
  //         console.error('Failed to fetch courses:', err)
  //         setCoursesLoading(false)
  //       })
  //   }
  // }, [token])

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
  setCoursesLoading(false)
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
        <Route path="/dashboard" element={<InstructorDashboardPage courses={courses} coursesLoading={coursesLoading}/>}/>
        <Route path="/student-submit" element={<StudentSubmitPage/>}/>
        <Route path="/course/:courseId" element={<CoursePage courses={courses} coursesLoading={coursesLoading}/>}/>
        <Route path="/course/:courseId/assignment/:assignmentId" element={<AssignmentDetailPage courses={courses} coursesLoading={coursesLoading}/>}/>
      </Routes>
      
    </div>
  )
}

export default App
