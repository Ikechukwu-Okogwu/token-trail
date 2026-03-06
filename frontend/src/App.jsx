import { useState, useEffect } from 'react'
import {Routes, Route} from 'react-router-dom'
import Sidebar from './components/Sidebar/Sidebar'
import LoginPage from './pages/LoginPage'
import InstructorDashboardPage from './pages/InstructorDashboardPage'
import StudentSubmitPage from './pages/StudentSubmitPage'
import AssignmentPage from './pages/AssignmentPage'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

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

  // useEffect(() => {
  //   fetch(`${API_BASE}/instructor/courses`)
  //     .then(r => r.json())
  //     .then(data => setCourses(data)) // adjust if wrapped
  // }, [])
  // document.getElementById("courses").innerHTML = courses;

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
        <Route path="/dashboard" element={<InstructorDashboardPage/>}/>
        <Route path="/student-submit" element={<StudentSubmitPage/>}/>
        
      </Routes>
      
    </div>
  )
}

export default App
