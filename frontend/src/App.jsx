import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import StudentSubmitPage from './pages/StudentSubmitPage'
import AssignmentDetailPage from './pages/AssignmentDetailPage'
import CoursePage from './pages/CoursePage'
import HomePage from './pages/HomePage'
import SimilarityReportPage from './pages/SimilarityReportPage'
import { getInstructorCourses } from './services/api'
import SimilarityPairDetailPage from './pages/SimilarityPairDetailPage'
import SimilarityComparisonPage from './pages/SimilarityComparisonPage'

function ProtectedRoute({ children }) {
  const [authorized, setAuthorized] = useState(null) // null = loading

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      setAuthorized(false)
      return
    }

    getInstructorCourses()
      .then(() => setAuthorized(true))
      .catch((err) => {
        if (err.status === 401) {
          localStorage.removeItem("token")
          setAuthorized(false)
        } else {
          setAuthorized(true) 
        }
      })
  }, [])

  if (authorized === null) {
    return <div>Loading...</div>
  }

  if (!authorized) {
    return <Navigate to="/login" replace />
  }

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
        <Route path="/similarity/:runId" element={<ProtectedRoute><SimilarityReportPage /></ProtectedRoute>}/>
        <Route path="/similarity/:runId/pair/:resultId" element={<ProtectedRoute><SimilarityPairDetailPage /></ProtectedRoute>}/>
        <Route path="/similarity/:runId/pair/:resultId/compare" element={<ProtectedRoute><SimilarityComparisonPage /></ProtectedRoute>}/>
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
    <div className="min-h-screen bg-gray-100 font-sans flex flex-col">

      <div className="bg-[#3b3660] px-6 py-4 flex-shrink-0">
        <span className="text-white text-xl font-bold">Token Trail</span>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-3">Welcome to Token Trail</h1>
          <p className="text-gray-500 text-base max-w-sm mx-auto">
            Code similarity detection for programming assignments. Who are you?
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-6 w-full max-w-lg">
          <a
            href="/student-submit"
            className="flex-1 bg-white border border-gray-200 rounded-2xl p-8 text-center no-underline text-gray-900 shadow-sm hover:shadow-md hover:border-[#3b3660] focus:outline-none focus:ring-2 focus:ring-[#3b3660] focus:ring-offset-2 transition-all group"
          >
            <div className="text-4xl mb-4">🎓</div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-[#3b3660] transition-colors">Student</h2>
            <p className="text-sm text-gray-500">Submit your assignment ZIP</p>
          </a>

          <a
            href="/login"
            className="flex-1 bg-white border border-gray-200 rounded-2xl p-8 text-center no-underline text-gray-900 shadow-sm hover:shadow-md hover:border-[#3b3660] focus:outline-none focus:ring-2 focus:ring-[#3b3660] focus:ring-offset-2 transition-all group"
          >
            <div className="text-4xl mb-4">🏫</div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-[#3b3660] transition-colors">Instructor</h2>
            <p className="text-sm text-gray-500">Manage courses and run analysis</p>
          </a>
        </div>
      </div>
    </div>
  )
}
