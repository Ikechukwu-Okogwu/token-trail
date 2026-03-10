<<<<<<< HEAD
import { useState, useEffect, Fragment } from 'react'
import {Routes, Route} from 'react-router-dom'
import Sidebar from './components/Sidebar/Sidebar'
import LoginPage from './pages/LoginPage'
import InstructorDashboardPage from './pages/InstructorDashboardPage'
import StudentSubmitPage from './pages/StudentSubmitPage'
import AssignmentPage from './pages/AssignmentPage'
import CoursePage from './pages/CoursePage'

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
        { id: "a1", title: "Assignment 1" },
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
        {courses.map((course) => (
          <Fragment key={course.id}>
            <Route path={`/course/${course.id}`} element={<CoursePage courses={courses}/>}/>
            {course.assignments.map((assignment) => (
              <Route key={assignment.id} path={`/course/${course.id}/assignment/${assignment.id}`} element={<AssignmentPage courses={courses}/>}/>
            ))}
          </Fragment>
        ))}
      </Routes>
      
=======
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import StudentSubmitPage from './pages/StudentSubmitPage'

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return children
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/*role selector (Student / Teacher) */}
        <Route path="/" element={<HomePage />} />

        {/* Teacher login/signup */}
        <Route path="/login" element={<LoginPage />} />

        {/*Student submit flow*/}
        <Route path="/submit" element={<StudentSubmitPage />} />

        {/*Catch-all*/}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

// -- Home screen - Student/Teacher selector ---- 
function HomePage() {
  return (
    <div style={styles.page}>

      {/* Top navigation bar */}
      <div style={styles.navbar}>
        <span style={styles.navTitle}>Token Trail</span>
      </div>

      {/* Two cards in the middle of the screen */}
      <div style={styles.cardRow}>

        {/* Student card — clicking this goes to /submit */}
        <a href="/submit" style={styles.card}>
          <h2 style={styles.cardTitle}>Student</h2>
          <p style={styles.cardSub}>Submit an Assignment</p>
        </a>

        {/* Teacher card — clicking this goes to /login */}
        <a href="/login" style={styles.card}>
          <h2 style={styles.cardTitle}>Teacher</h2>
          <p style={styles.cardSub}>Login as Teacher</p>
        </a>

      </div>
>>>>>>> d66097a (Implement routing and protected routes in App component)
    </div>
  )
}

// Styles for the home page
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
    textAlign: 'center',
    textDecoration: 'none',
    color: '#1a1a1a',
    cursor: 'pointer',
  },
  cardTitle: {
    fontSize: '22px',
    margin: '0 0 12px 0',
  },
  cardIcon: {
    fontSize: '48px',
    margin: '0 0 12px 0',
  },
  cardSub: {
    fontSize: '13px',
    color: '#3a3a5c',
    margin: 0,
  },
}

export default App
