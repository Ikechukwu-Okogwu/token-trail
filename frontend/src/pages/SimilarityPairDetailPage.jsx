import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getSimilarityPairDetail } from '../services/api'
import Sidebar from '../components/Sidebar/Sidebar'

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

          {loading && <p className="text-gray-400 text-sm mt-4">Loading…</p>}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm mt-4">{error}</div>
          )}

          {data && (
            <div className="mt-4 space-y-3">
              <Row label="Similarity Score">
                <span className={`text-2xl font-bold ${data.similarityScore >= 0.8 ? 'text-red-500' : data.similarityScore >= 0.5 ? 'text-yellow-600' : 'text-green-600'}`}>
                  {(data.similarityScore * 100).toFixed(1)}%
                </span>
              </Row>
              <Row label="Submission A"><code className="text-sm font-mono text-gray-700">{data.leftSubmissionId}</code></Row>
              <Row label="Submission B"><code className="text-sm font-mono text-gray-700">{data.rightSubmissionId}</code></Row>
              <Row label="Run ID"><code className="text-sm font-mono text-gray-500">{data.runId}</code></Row>
              {data.summary && <Row label="Note"><span className="text-sm text-gray-500">{data.summary}</span></Row>}

              <div className="pt-4">
                <button
                  onClick={() => navigate(`/similarity/${runId}/pair/${resultId}/compare`)}
                  className="bg-[#3b3660] text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-[#2d2b4a] transition-colors"
                >
                  Open Comparison →
                </button>
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
