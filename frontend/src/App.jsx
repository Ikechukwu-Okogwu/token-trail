import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import StudentSubmitPage from './pages/StudentSubmitPage'
import AssignmentDetailPage from './pages/AssignmentDetailPage'
import CoursePage from './pages/CoursePage'
import HomePage from './pages/HomePage'

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return children
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export default function App() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((res) => res.json())
      .then(setHealth)
      .catch(console.error)
  }, [])

  function handleLogout() {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <HomePage onLogout={handleLogout} />
            </ProtectedRoute>
          }
        />
        <Route path="/student-submit" element={<StudentSubmitPage/>}/>
        <Route path="/course/:courseId" element={<CoursePage/>}/>
        <Route path="/course/:courseId/assignment/:assignmentId" element={<AssignmentDetailPage/>}/>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {health && (
        <div className="fixed bottom-2 right-3 text-xs text-gray-400 select-none">
          API: {health.status}
        </div>
      )}
    </>
  )
}

function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-200 font-sans">
      <div className="bg-[#3d3d5c] px-6 py-4">
        <span className="text-white text-xl font-bold">Token Trail</span>
      </div>

      <div className="flex justify-center items-center gap-8 mt-20">
        <a
          href="/student-submit"
          className="bg-[#b8a9d4] border-2 border-dashed border-[#8a7aaa] rounded-2xl p-10 w-52 text-center no-underline text-gray-900 cursor-pointer hover:shadow-lg transition-shadow"
        >
          <h2 className="text-xl font-bold mb-3">Student</h2>
          <p className="text-sm text-[#3a3a5c]">Submit an Assignment</p>
        </a>

        <a
          href="/login"
          className="bg-[#b8a9d4] border-2 border-dashed border-[#8a7aaa] rounded-2xl p-10 w-52 text-center no-underline text-gray-900 cursor-pointer hover:shadow-lg transition-shadow"
        >
          <h2 className="text-xl font-bold mb-3">Teacher</h2>
          <p className="text-sm text-[#3a3a5c]">Login as Teacher</p>
        </a>
      </div>
    </div>
  )
}
