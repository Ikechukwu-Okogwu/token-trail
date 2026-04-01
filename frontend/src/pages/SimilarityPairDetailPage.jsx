import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getSimilarityPairDetail } from '../services/api'
import Sidebar from '../components/Sidebar/Sidebar'
import Button from '../components/ui/Button'
import { ScoreBadge } from '../components/ui/Badge'
import ErrorBanner from '../components/ui/ErrorBanner'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import { ArrowLeft, User, ChevronRight, Info } from 'lucide-react'

function scoreLabel(score) {
  if (score >= 0.8) return { text: 'High similarity — review recommended', color: 'text-red-600', bg: 'bg-red-50 border-red-200' }
  if (score >= 0.5) return { text: 'Medium similarity', color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200' }
  return { text: 'Low similarity', color: 'text-green-600', bg: 'bg-green-50 border-green-200' }
}

export default function SimilarityPairDetailPage() {
  const { runId, resultId } = useParams()
  const navigate = useNavigate()
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(null)

  useEffect(() => {
    setLoading(true)
    getSimilarityPairDetail(decodeURIComponent(resultId))
      .then(setData)
      .catch((err) => setError(err.message || 'Failed to load pair detail.'))
      .finally(() => setLoading(false))
  }, [resultId])

  const label = data ? scoreLabel(data.similarityScore) : null

  return (
    <div className="h-screen flex">
      <Sidebar />
      <main className="ml-55 flex-1 overflow-y-auto bg-brand-pink/40">
        <div className="mx-auto max-w-3xl p-6 lg:p-8">

          {/* Back */}
          <Link
            to={`/similarity/${runId}`}
            className="mb-5 inline-flex items-center gap-1.5 text-sm text-brand-purple hover:underline"
          >
            <ArrowLeft className="h-4 w-4" /> Back to Results
          </Link>

          {loading && <LoadingSpinner message="Loading…" />}
          {error && <ErrorBanner message={error} />}

          {data && (
            <>
              {/* Header */}
              <div className="mb-5">
                <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-brand-purple/60">
                  Submission Pair
                </p>
                <h1 className="text-2xl font-bold text-gray-900">Pair Detail</h1>
                <p className="mt-1 text-sm text-gray-400">
                  Review submission metadata before opening the comparison.
                </p>
              </div>

              {/* Score banner */}
              <div className={`mb-5 flex items-center gap-4 rounded-2xl border px-5 py-4 ${label.bg}`}>
                <div>
                  <div className="text-3xl font-bold tabular-nums leading-none" style={{ color: 'inherit' }}>
                    <ScoreBadge score={data.similarityScore} />
                  </div>
                </div>
                <div>
                  <p className={`font-semibold text-sm ${label.color}`}>{label.text}</p>
                  {data.summary && <p className="mt-0.5 text-xs text-gray-500">{data.summary}</p>}
                </div>
                <div className="ml-auto">
                  <Button
                    size="lg"
                    onClick={() => navigate(`/similarity/${runId}/pair/${resultId}/compare`)}
                  >
                    Open Comparison <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Student cards */}
              <div className="mb-5 grid grid-cols-2 gap-4">
                {[
                  { label: 'Student A', name: data.leftStudentName, id: data.leftStudentIdentifier, subId: data.leftSubmissionId },
                  { label: 'Student B', name: data.rightStudentName, id: data.rightStudentIdentifier, subId: data.rightSubmissionId },
                ].map(s => (
                  <div key={s.label} className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
                    <div className="mb-3 flex items-center gap-2.5">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-purple/10">
                        <User className="h-4 w-4 text-brand-purple" />
                      </div>
                      <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">{s.label}</span>
                    </div>
                    <p className="text-base font-bold text-gray-900">{s.name || <span className="font-normal italic text-gray-400">Unnamed</span>}</p>
                    <p className="mt-0.5 font-mono text-sm text-gray-500">{s.id || '—'}</p>
                    <p className="mt-2 font-mono text-[11px] text-gray-400 truncate">Sub: {s.subId}</p>
                  </div>
                ))}
              </div>

              {/* Run info */}
              <div className="mb-5 rounded-xl border border-gray-200 bg-white px-5 py-3.5 shadow-sm">
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-gray-400 uppercase tracking-wide font-semibold w-20 shrink-0">Run ID</span>
                  <code className="font-mono text-gray-600">{data.runId}</code>
                </div>
              </div>

              {/* Disclaimer */}
              <div className="flex items-start gap-2.5 rounded-xl border border-gray-200 bg-white px-4 py-3 text-xs text-gray-500 shadow-sm">
                <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-gray-400" />
                <span>
                  <span className="font-semibold text-gray-600">Note: </span>
                  Similarity scores indicate structural overlap and are not proof of misconduct.
                </span>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
