import { useEffect, useState, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getSimilarityResults, getAnalysisRunStatus } from '../services/api'
import Sidebar from '../components/Sidebar/Sidebar'
import { StatusBadge } from '../components/ui/Badge'
import ErrorBanner from '../components/ui/ErrorBanner'
import WarningBanner from '../components/ui/WarningBanner'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import {
  AlertTriangle, Search, ArrowUpDown, ArrowUp, ArrowDown,
  Users, GitCompare, Flag, TrendingUp, ChevronRight, Info, ArrowLeft
} from 'lucide-react'

const THRESHOLDS = [
  { label: 'All results', value: 0 },
  { label: '> 40%', value: 0.4 },
  { label: '> 60%', value: 0.6 },
  { label: '> 80%', value: 0.8 },
  { label: '> 90%', value: 0.9 },
]

function scoreLabel(score) {
  if (score >= 0.8) return { text: 'High', cls: 'bg-red-50 text-red-600 border border-red-200' }
  if (score >= 0.5) return { text: 'Medium', cls: 'bg-amber-50 text-amber-700 border border-amber-200' }
  return { text: 'Low', cls: 'bg-green-50 text-green-700 border border-green-200' }
}

function truncateId(value) {
  if (!value) return value
  return value.length > 16 ? value.slice(0, 8) + '…' : value
}

function ScoreBar({ score }) {
  const pct = Math.round(score * 100)
  const color = score >= 0.8 ? 'bg-red-500' : score >= 0.5 ? 'bg-amber-400' : 'bg-green-500'
  return (
    <div className="flex items-center gap-2.5 min-w-[140px]">
      <span className={`text-base font-bold tabular-nums w-12 shrink-0 ${score >= 0.8 ? 'text-red-600' : score >= 0.5 ? 'text-amber-600' : 'text-green-600'}`}>
        {pct}%
      </span>
      <div className="flex-1 h-1.5 rounded-full bg-gray-100 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, accent }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3.5 shadow-sm">
      <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${accent}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div>
        <div className="text-xl font-bold text-gray-900 leading-none">{value}</div>
        <div className="mt-0.5 text-xs text-gray-500">{label}</div>
      </div>
    </div>
  )
}

export default function SimilarityReportPage() {
  const { runId } = useParams()
  const [data, setData]       = useState(null)
  const [runInfo, setRunInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [search, setSearch]   = useState('')
  const [threshold, setThreshold] = useState(0)
  const [sortDir, setSortDir] = useState('desc')
  const [viewMode, setViewMode] = useState('detailed')

  useEffect(() => {
    setLoading(true)
    Promise.all([
      getSimilarityResults(runId),
      getAnalysisRunStatus(runId).catch(() => null),
    ])
      .then(([results, info]) => {
        setData(results)
        setRunInfo(info)
      })
      .catch((err) => setError(err.message || 'Failed to load results.'))
      .finally(() => setLoading(false))
  }, [runId])

  const results = data?.results ?? []

  const stats = useMemo(() => {
    if (!results.length) return { submissions: 0, comparisons: 0, flagged: 0, highest: 0 }
    const unique = new Set(results.flatMap(r => [r.leftSubmissionId, r.rightSubmissionId]))
    return {
      submissions: unique.size,
      comparisons: results.length,
      flagged: results.filter(r => r.similarityScore >= 0.8).length,
      highest: Math.max(...results.map(r => r.similarityScore)),
    }
  }, [results])

  const filtered = useMemo(() => {
    const q = search.toLowerCase()
    return results
      .filter(r => r.similarityScore >= threshold)
      .filter(r => !q || [
        r.leftStudentName, r.leftStudentIdentifier,
        r.rightStudentName, r.rightStudentIdentifier,
      ].some(v => v?.toLowerCase().includes(q)))
      .sort((a, b) => sortDir === 'desc'
        ? b.similarityScore - a.similarityScore
        : a.similarityScore - b.similarityScore)
  }, [results, threshold, search, sortDir])

  const toggleSort = () => setSortDir(d => d === 'desc' ? 'asc' : 'desc')
  const toggleViewMode = () => setViewMode(m => m === 'detailed' ? 'compact' : 'detailed')
  const isCompact = viewMode === 'compact'
  const backPath = runInfo?.courseId && runInfo?.assignmentId
    ? `/course/${runInfo.courseId}/assignment/${runInfo.assignmentId}`
    : '/dashboard'

  return (
    <div className="h-screen flex">
      <Sidebar />
      <main className="ml-55 flex-1 overflow-y-auto bg-brand-pink/40">
        <div className="mx-auto max-w-6xl p-6 lg:p-8">
          <Link
            to={backPath}
            className="mb-3 inline-flex items-center gap-1.5 text-sm text-gray-400 no-underline transition-colors hover:text-brand-purple"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Assignment Details
          </Link>

          {/* Header */}
          <div className="mb-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Analysis Results</h1>
                <p className="mt-1 text-sm text-gray-400">
                  Review similarity scores and investigate flagged submissions.
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {runInfo?.status && <StatusBadge status={runInfo.status} />}
                {runInfo?.finishedAt && (
                  <span className="text-xs text-gray-400">
                    {new Date(runInfo.finishedAt).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
          </div>

          {loading && <LoadingSpinner message="Loading results…" />}
          <ErrorBanner message={error} />

          {!loading && !error && data && (
            <>
              {/* Stats row */}
              <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <StatCard icon={Users}      label="Submissions"   value={stats.submissions} accent="bg-brand-purple/10 text-brand-purple" />
                <StatCard icon={GitCompare} label="Comparisons"   value={stats.comparisons} accent="bg-brand-purple/10 text-brand-purple" />
                <StatCard icon={Flag}       label="Flagged (≥80%)" value={stats.flagged}    accent={stats.flagged > 0 ? 'bg-red-50 text-red-500' : 'bg-gray-100 text-gray-400'} />
                <StatCard icon={TrendingUp} label="Highest Score"  value={stats.highest > 0 ? `${Math.round(stats.highest * 100)}%` : '—'} accent={stats.highest >= 0.8 ? 'bg-red-50 text-red-500' : 'bg-green-50 text-green-600'} />
              </div>

              {/* Run warnings */}
              {runInfo?.warnings?.length > 0 && (
                <div className="mb-4">
                  <WarningBanner warnings={runInfo.warnings} />
                </div>
              )}

              {/* Controls */}
              <div className="mb-4 flex flex-wrap items-center gap-3">
                <div className="relative flex-1 min-w-[200px] max-w-xs">
                  <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by student name or ID…"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="h-9 w-full rounded-xl border border-gray-200 bg-white pl-9 pr-3 text-sm text-gray-700 placeholder-gray-400 shadow-sm outline-none transition focus:border-brand-purple/40 focus:ring-2 focus:ring-brand-purple/10"
                  />
                </div>
                <select
                  value={threshold}
                  onChange={e => setThreshold(Number(e.target.value))}
                  className="h-9 rounded-xl border border-gray-200 bg-white px-3 text-sm text-gray-700 shadow-sm outline-none focus:border-brand-purple/40 focus:ring-2 focus:ring-brand-purple/10"
                >
                  {THRESHOLDS.map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
                <button
                  onClick={toggleSort}
                  className="inline-flex h-9 items-center gap-1.5 rounded-xl border border-gray-200 bg-white px-3 text-sm text-gray-600 shadow-sm transition hover:bg-gray-50"
                >
                  {sortDir === 'desc' ? <ArrowDown className="h-3.5 w-3.5" /> : <ArrowUp className="h-3.5 w-3.5" />}
                  Score {sortDir === 'desc' ? 'High → Low' : 'Low → High'}
                </button>
                <button
                  onClick={toggleViewMode}
                  className="inline-flex h-9 items-center gap-1.5 rounded-xl border border-gray-200 bg-white px-3 text-sm text-gray-600 shadow-sm transition hover:bg-gray-50"
                >
                  {isCompact ? 'Detailed View' : 'Compact View'}
                </button>
                <span className="ml-auto text-xs text-gray-400">
                  {filtered.length} of {results.length} result{results.length !== 1 ? 's' : ''}
                </span>
              </div>

              {/* Table */}
              {filtered.length === 0 ? (
                <div className="flex flex-col items-center justify-center rounded-2xl border border-gray-200 bg-white py-16 text-center shadow-sm">
                  <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-purple/10">
                    <GitCompare className="h-6 w-6 text-brand-purple/50" />
                  </div>
                  <p className="text-sm font-semibold text-gray-600">No results match your filters</p>
                  <p className="mt-1 text-xs text-gray-400">Try lowering the threshold or clearing the search.</p>
                </div>
              ) : (
                <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      <tr className="border-b border-gray-100 bg-gray-50/80">
                        <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-400 w-8">#</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-400">Student A</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-400">Student B</th>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-400">
                          <button onClick={toggleSort} className="inline-flex items-center gap-1 hover:text-gray-600 transition-colors">
                            Similarity <ArrowUpDown className="h-3 w-3" />
                          </button>
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-400">Status</th>
                        <th className="px-4 py-3" />
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {filtered.map((row, i) => {
                        const { text, cls } = scoreLabel(row.similarityScore)
                        return (
                          <tr key={row.resultId} className="group transition-colors hover:bg-brand-purple/[0.025]">
                            <td className="px-5 py-3.5 text-xs text-gray-400 tabular-nums">{i + 1}</td>
                            <td className="px-4 py-3.5">
                              <div className="font-semibold text-gray-900">
                                {truncateId(row.leftStudentName) || <span className="text-gray-400 font-normal italic">Unnamed</span>}
                              </div>
                              {!isCompact && (
                                <div className="text-xs text-gray-400 font-mono mt-0.5" title={row.leftStudentIdentifier}>{truncateId(row.leftStudentIdentifier) || '—'}</div>
                              )}
                            </td>
                            <td className="px-4 py-3.5">
                              <div className="font-semibold text-gray-900">
                                {truncateId(row.rightStudentName) || <span className="text-gray-400 font-normal italic">Unnamed</span>}
                              </div>
                              {!isCompact && (
                                <div className="text-xs text-gray-400 font-mono mt-0.5" title={row.rightStudentIdentifier}>{truncateId(row.rightStudentIdentifier) || '—'}</div>
                              )}
                            </td>
                            <td className="px-4 py-3.5">
                              <ScoreBar score={row.similarityScore} />
                            </td>
                            <td className="px-4 py-3.5">
                              <div className="flex items-center gap-1.5">
                                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
                                  {row.similarityScore >= 0.8 && (
                                    <AlertTriangle className="mr-1 h-3 w-3" />
                                  )}
                                  {text}
                                </span>
                                {row.warnings?.length > 0 && (
                                  <span title={row.warnings.join('; ')} className="inline-flex items-center rounded-full bg-amber-50 border border-amber-200 px-1.5 py-0.5 text-[10px] font-semibold text-amber-600 cursor-help">
                                    <AlertTriangle className="mr-0.5 h-2.5 w-2.5" />
                                    !
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="px-4 py-3.5">
                              <Link
                                to={`/similarity/${runId}/pair/${encodeURIComponent(row.resultId)}`}
                                className="inline-flex items-center gap-1 rounded-lg bg-brand-purple px-3 py-1.5 text-xs font-semibold text-white opacity-90 transition hover:opacity-100 hover:shadow-sm group-hover:opacity-100"
                              >
                                View Details <ChevronRight className="h-3.5 w-3.5" />
                              </Link>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Disclaimer */}
              <div className="mt-5 flex items-start gap-2.5 rounded-xl border border-gray-200 bg-white px-4 py-3 text-xs text-gray-500 shadow-sm">
                <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-gray-400" />
                <span>
                  <span className="font-semibold text-gray-600">Note: </span>
                  Similarity scores indicate structural overlap between submissions and are not proof of misconduct.
                  Review the full comparison before drawing conclusions.
                </span>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
