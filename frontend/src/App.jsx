import { useState, useEffect } from 'react'
import { Routes, Route, Navigate, useLocation, Link } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
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
  const [authorized, setAuthorized] = useState(null)
  const pageLocation = useLocation()

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
  }, [pageLocation])

  if (authorized === null) {
    return (
      <div className="h-screen flex items-center justify-center bg-brand-pink/40">
        <span className="text-sm text-gray-400">Loading…</span>
      </div>
    )
  }

  if (!authorized) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm px-4 py-10">
        <div className="mx-auto w-full max-w-lg rounded-[2rem] bg-white/95 p-8 shadow-2xl ring-1 ring-slate-900/10">
          <h2 className="text-2xl font-semibold text-slate-900">Login required</h2>
          <p className="mt-3 text-sm leading-6 text-slate-700">
            Your session is missing or expired, or you do not have access to this page.
            Please login to continue.
          </p>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Link
              to="/login"
              className="inline-flex justify-center rounded-full bg-brand-purple px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
            >
              Go to login
            </Link>
            <Link
              to="/"
              className="inline-flex justify-center rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
            >
              Return home
            </Link>
          </div>
        </div>
      </div>
    )
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

  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route path="/student-submit" element={<StudentSubmitPage/>}/>
        <Route path="/course/:courseId" element={<ProtectedRoute><CoursePage/></ProtectedRoute>}/>
        <Route path="/course/:courseId/assignment/:assignmentId" element={<ProtectedRoute><AssignmentDetailPage/></ProtectedRoute>}/>
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

