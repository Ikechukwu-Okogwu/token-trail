import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getSimilarityResults } from '../services/api'
import Sidebar from '../components/Sidebar/Sidebar'
import { ScoreBadge } from '../components/ui/Badge'
import ErrorBanner from '../components/ui/ErrorBanner'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import EmptyState from '../components/ui/EmptyState'

export default function SimilarityReportPage() {
  const { runId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    getSimilarityResults(runId)
      .then(setData)
      .catch((err) => setError(err.message || 'Failed to load similarity results.'))
      .finally(() => setLoading(false))
  }, [runId])

  return (
    <div className="h-screen flex">
      <Sidebar />
      <main className="ml-55 flex-1 p-6">
        <div className="bg-white rounded-2xl shadow-sm p-6 min-h-full">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Similarity Results</h2>
          <p className="text-sm text-gray-500 mb-6">Run ID: {runId}</p>

          {loading && <LoadingSpinner message="Loading results…" />}
          <ErrorBanner message={error} />

          {data && data.results.length === 0 && (
            <EmptyState message="No similarity pairs found for this run." />
          )}

          {data && data.results.length > 0 && (
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-200 text-left text-gray-500 text-xs uppercase tracking-wide">
                  <th className="pb-3 pr-4">Rank</th>
                  <th className="pb-3 pr-4">Submission A</th>
                  <th className="pb-3 pr-4">Submission B</th>
                  <th className="pb-3 pr-4">Score</th>
                  <th className="pb-3"></th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((row, i) => (
                  <tr key={row.resultId} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 pr-4 text-gray-400">{i + 1}</td>
                    <td className="py-3 pr-4 font-mono text-gray-700">{row.leftSubmissionId.slice(-8)}</td>
                    <td className="py-3 pr-4 font-mono text-gray-700">{row.rightSubmissionId.slice(-8)}</td>
                    <td className="py-3 pr-4">
                      <ScoreBadge score={row.similarityScore} />
                    </td>
                    <td className="py-3">
                      <Link
                        to={`/similarity/${runId}/pair/${encodeURIComponent(row.resultId)}`}
                        className="text-[#3b3660] text-xs font-semibold hover:underline"
                      >
                        View →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  )
}
