import { useState, useEffect, Fragment } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar/Sidebar'
import LoginPage from './pages/LoginPage'
import InstructorDashboardPage from './pages/InstructorDashboardPage'
import StudentSubmitPage from './pages/StudentSubmitPage'
import AssignmentPage from './pages/AssignmentPage'
import CoursePage from './pages/CoursePage'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return children
}

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

  useEffect(() => {
    setCourses([
      {id:"1", name:"COSC 4P02", assignments: [
        { id: "a1", title: "Assignment 1" },
        { id: "a2", title: "Assignment 2" },
        { id: "a3", title: "Assignment 3" },
      ]},
      {id:"2", name:"COSC 4P01", assignments:[]}
    ])
  }, [])

  if (loading) return <p>Loading...</p>
  if (error) return <p>Error: {error}</p>

  return (
    <div>
      <Routes>
        {/* Home screen Student / Teacher selector */}
        <Route path="/" element={<HomePage />} />

        {/* Teacher login*/}
        <Route path="/login" element={<LoginPage />} />

        {/* Student submit flow */}
        <Route path="/student-submit" element={<StudentSubmitPage />} />
        <Route path="/submit" element={<StudentSubmitPage />} />

        {/* Instructor dashboard */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <InstructorDashboardPage courses={courses} />
          </ProtectedRoute>
        }/>

        {/* Course and assignment pages */}
        {courses.map((course) => (
          <Fragment key={course.id}>
            <Route path={`/course/${course.id}`} element={
              <ProtectedRoute>
                <CoursePage courses={courses} />
              </ProtectedRoute>
            }/>
            {course.assignments.map((assignment) => (
              <Route key={assignment.id} path={`/course/${course.id}/assignment/${assignment.id}`} element={
                <ProtectedRoute>
                  <AssignmentPage courses={courses} />
                </ProtectedRoute>
              }/>
            ))}
          </Fragment>
        ))}

        {/*catch-all*/}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

// Home screen Student / Teacher selector
function HomePage() {
  return (
    <div style={styles.page}>
      <div style={styles.navbar}>
        <span style={styles.navTitle}>Token Trail</span>
      </div>
      <div style={styles.cardRow}>
        <a href="/submit" style={styles.card}>
          <h2 style={styles.cardTitle}>Student</h2>
          <p style={styles.cardSub}>Submit an Assignment</p>
        </a>
        <a href="/login" style={styles.card}>
          <h2 style={styles.cardTitle}>Teacher</h2>
          <p style={styles.cardSub}>Login as Teacher</p>
        </a>
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    backgroundColor: '#e0e0e0',
    fontFamily: 'sans-serif',
  },
  navbar: {
    backgroundColor: '#3d3d5c',
    padding: '16px 24px',
  },
  navTitle: {
    color: 'white',
    fontSize: '20px',
    fontWeight: 'bold',
  },
  cardRow: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '32px',
    marginTop: '80px',
  },
  card: {
     backgroundColor: '#b8a9d4',
    border: '2px dashed #8a7aaa',
    borderRadius: '16px',
    padding: '40px',
    width: '200px',
    height: '160px',
    textAlign: 'center',
    textDecoration: 'none',
    color: '#1a1a1a',
    cursor: 'pointer',
  },
  cardTitle: {
    fontSize: '22px',
    margin: '0 0 12px 0',
  },
  cardSub: {
    fontSize: '13px',
    color: '#3a3a5c',
    margin: 0,
  },
}

export default App