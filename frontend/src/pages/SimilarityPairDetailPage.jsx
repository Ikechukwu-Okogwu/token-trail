import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getSimilarityPairDetail } from '../services/api'
import Sidebar from '../components/Sidebar/Sidebar'
import Button from '../components/ui/Button'
import { ScoreBadge } from '../components/ui/Badge'
import ErrorBanner from '../components/ui/ErrorBanner'
import LoadingSpinner from '../components/ui/LoadingSpinner'

export default function SimilarityPairDetailPage() {
  const { runId, resultId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    getSimilarityPairDetail(decodeURIComponent(resultId))
      .then(setData)
      .catch((err) => setError(err.message || 'Failed to load pair detail.'))
      .finally(() => setLoading(false))
  }, [resultId])

  return (
    <div className="h-screen flex">
      <Sidebar />
      <main className="ml-55 flex-1 p-6">
        <div className="bg-white rounded-2xl shadow-sm p-6 min-h-full">
          <Link to={`/similarity/${runId}`} className="text-sm text-[#3b3660] hover:underline">
            ← Back to results
          </Link>
          <h2 className="text-xl font-bold text-gray-900 mt-4 mb-1">Pair Detail</h2>

          {loading && <LoadingSpinner message="Loading…" />}
          {error && <ErrorBanner message={error} />}

          {data && (
            <div className="mt-4 space-y-3">
              <Row label="Similarity Score">
                <ScoreBadge score={data.similarityScore} />
              </Row>
              <Row label="Submission A"><code className="text-sm font-mono text-gray-700">{data.leftSubmissionId}</code></Row>
              <Row label="Student ID A"><code className="text-sm font-mono text-gray-700">{data.leftStudentIdentifier || 'N/A'}</code></Row>
              <Row label="Student Name A"><span className="text-sm text-gray-700">{data.leftStudentName || 'N/A'}</span></Row>
              <Row label="Submission B"><code className="text-sm font-mono text-gray-700">{data.rightSubmissionId}</code></Row>
              <Row label="Student ID B"><code className="text-sm font-mono text-gray-700">{data.rightStudentIdentifier || 'N/A'}</code></Row>
              <Row label="Student Name B"><span className="text-sm text-gray-700">{data.rightStudentName || 'N/A'}</span></Row>
              <Row label="Run ID"><code className="text-sm font-mono text-gray-500">{data.runId}</code></Row>
              {data.summary && <Row label="Note"><span className="text-sm text-gray-500">{data.summary}</span></Row>}

              <div className="pt-4">
                <Button onClick={() => navigate(`/similarity/${runId}/pair/${resultId}/compare`)}>
                  Open Comparison →
                </Button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

function Row({ label, children }) {
  return (
    <div className="flex items-start gap-4 border-b border-gray-100 pb-3">
      <span className="w-40 text-xs text-gray-400 uppercase tracking-wide flex-shrink-0 pt-0.5">{label}</span>
      <div>{children}</div>
    </div>
  )
}
