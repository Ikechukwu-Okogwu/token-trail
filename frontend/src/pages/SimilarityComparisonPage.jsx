import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getSimilarityComparison } from '../services/api'
import Sidebar from '../components/Sidebar/Sidebar'
import ErrorBanner from '../components/ui/ErrorBanner'
import LoadingSpinner from '../components/ui/LoadingSpinner'

export default function SimilarityComparisonPage() {
  const { runId, resultId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    getSimilarityComparison(decodeURIComponent(resultId))
      .then(setData)
      .catch((err) => setError(err.message || 'Failed to load comparison.'))
      .finally(() => setLoading(false))
  }, [resultId])

  return (
    <div className="h-screen flex">
      <Sidebar />
      <main className="ml-55 flex-1 flex flex-col p-6 overflow-hidden">
        <div className="bg-white rounded-2xl shadow-sm p-4 mb-3 flex items-center gap-4 flex-shrink-0">
          <Link to={`/similarity/${runId}/pair/${resultId}`} className="text-sm text-[#3b3660] hover:underline">
            ← Back to pair
          </Link>
          <span className="text-sm font-semibold text-gray-700">Side-by-Side Comparison</span>
          {data && (
            <span className={`ml-auto text-lg font-bold ${data.similarityScore >= 0.8 ? 'text-red-500' : data.similarityScore >= 0.5 ? 'text-yellow-600' : 'text-green-600'}`}>
              {(data.similarityScore * 100).toFixed(1)}% similar
            </span>
          )}
        </div>

        {loading && <LoadingSpinner message="Loading comparison…" />}
        {error && <ErrorBanner message={error} />}

        {data && (
          <div className="flex gap-3 flex-1 overflow-hidden">
            <CodePane
              title={`Submission A — ${data.leftSubmissionId.slice(-8)}`}
              submissionId={data.leftSubmissionId}
              studentIdentifier={data.leftStudentIdentifier}
              studentName={data.leftStudentName}
              code={data.leftCode}
              filePath={data.leftFilePath}
            />
            <CodePane
              title={`Submission B — ${data.rightSubmissionId.slice(-8)}`}
              submissionId={data.rightSubmissionId}
              studentIdentifier={data.rightStudentIdentifier}
              studentName={data.rightStudentName}
              code={data.rightCode}
              filePath={data.rightFilePath}
            />
          </div>
        )}
      </main>
    </div>
  )
}

function CodePane({ title, submissionId, studentIdentifier, studentName, code, filePath }) {
  const lines = (code || '').split('\n')
  return (
    <div className="flex-1 flex flex-col bg-gray-950 rounded-xl overflow-hidden">
      <div className="px-4 py-2 bg-gray-900 flex-shrink-0">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="text-xs font-semibold text-gray-300">{title}</div>
            <div className="text-[11px] text-gray-400 font-mono truncate">Submission ID: {submissionId || 'N/A'}</div>
            <div className="text-[11px] text-gray-400 font-mono truncate">Student ID: {studentIdentifier || 'N/A'}</div>
            <div className="text-[11px] text-gray-400 truncate">Student Name: {studentName || 'N/A'}</div>
          </div>
          {filePath && (
            <span className="text-xs text-gray-500 ml-2 font-mono flex-shrink-0">
              {filePath.split('/').pop() || filePath}
            </span>
          )}
        </div>
      </div>
      {!code ? (
        <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">No source available</div>
      ) : (
        <div className="flex-1 overflow-auto">
          <table className="text-xs font-mono w-full border-collapse">
            <tbody>
              {lines.map((line, i) => (
                <tr key={i} className="hover:bg-gray-800">
                  <td className="select-none text-gray-600 text-right pr-3 pl-3 w-10 border-r border-gray-800">{i + 1}</td>
                  <td className="pl-3 pr-4 text-gray-200 whitespace-pre">{line}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
