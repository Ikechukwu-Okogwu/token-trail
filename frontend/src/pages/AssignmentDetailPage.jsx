import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  getAnalysisRunStatus,
  getAssignmentSubmissions,
  getInstructorAssignmentById,
  queueAnalysisRun,
} from '../services/api'
import Sidebar from '../components/Sidebar/Sidebar'
import Button from '../components/ui/Button'
import { StatusBadge } from '../components/ui/Badge'
import ErrorBanner from '../components/ui/ErrorBanner'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import EmptyState from '../components/ui/EmptyState'

function mapApiError(error, fallback) {
  const message = error?.message || ''
  const normalized = message.toLowerCase()

  if (normalized.includes('401') || normalized.includes('unauthorized')) {
    return 'Your session is missing or expired. Log in again and retry.'
  }
  if (normalized.includes('403') || normalized.includes('not your assignment')) {
    return "You do not have permission to access this assignment."
  }
  if (normalized.includes('404') && normalized.includes('analysis run')) {
    return 'Analysis run not found. Queue a new run or check the run ID.'
  }
  if (
    normalized.includes('404') ||
    normalized.includes('assignment not found')
  ) {
    return 'Assignment not found. Check the assignment ID and try again.'
  }

  return message || fallback
}

function formatDate(value) {
  if (!value) return 'N/A'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

export default function AssignmentDetailPage() {
  const { assignmentId } = useParams()
  const navigate = useNavigate()
  const [assignment, setAssignment] = useState(null)
  const [submissions, setSubmissions] = useState([])

  const [loadingAssignmentData, setLoadingAssignmentData] = useState(false)
  const [assignmentError, setAssignmentError] = useState(null)
  const [submissionsError, setSubmissionsError] = useState(null)
  const [pageError, setPageError] = useState(null)

  const [queueLoading, setQueueLoading] = useState(false)
  const [queueError, setQueueError] = useState(null)

  const [currentRun, setCurrentRun] = useState(null)
  const [runStatus, setRunStatus] = useState(null)
  const [statusLoading, setStatusLoading] = useState(false)
  const [statusError, setStatusError] = useState(null)
  const [isPolling, setIsPolling] = useState(false)

  const hasLoadedAssignment = Boolean(assignment?.id)
  const hasRun = Boolean(currentRun?.runId)
  const terminalRunState =
    runStatus?.status === 'completed' || runStatus?.status === 'failed'

  const refreshRunStatus = useCallback(
    async ({ silent = false } = {}) => {
      if (!currentRun?.runId) return

      if (!silent) setStatusLoading(true)
      setStatusError(null)

      try {
        const latest = await getAnalysisRunStatus(currentRun.runId)
        setRunStatus(latest)
      } catch (error) {
        setStatusError(
          mapApiError(error, 'Could not refresh analysis run status.')
        )
      } finally {
        if (!silent) setStatusLoading(false)
      }
    },
    [currentRun?.runId]
  )

  useEffect(() => {
    if (!isPolling || !currentRun?.runId) return undefined
    if (terminalRunState) return undefined

    const timer = setInterval(() => {
      refreshRunStatus({ silent: true })
    }, 3000)

    return () => clearInterval(timer)
  }, [currentRun?.runId, isPolling, refreshRunStatus, terminalRunState])

  useEffect(() => {
    if (terminalRunState) {
      setIsPolling(false)
    }
  }, [terminalRunState])

  useEffect(() => {
    if (!assignmentId) return

    setLoadingAssignmentData(true)
    setPageError(null)
    setAssignmentError(null)
    setSubmissionsError(null)
    setQueueError(null)
    setStatusError(null)
    setCurrentRun(null)
    setRunStatus(null)
    setIsPolling(false)

    const loadData = async () => {
      const [assignmentResult, submissionsResult] = await Promise.allSettled([
        getInstructorAssignmentById(assignmentId),
        getAssignmentSubmissions(assignmentId),
      ])

      if (assignmentResult.status === 'fulfilled') {
        setAssignment(assignmentResult.value)
      } else {
        setAssignment(null)
        setAssignmentError(
          mapApiError(
            assignmentResult.reason,
            'Could not load assignment details.'
          )
        )
      }

      if (submissionsResult.status === 'fulfilled') {
        setSubmissions(submissionsResult.value)
      } else {
        setSubmissions([])
        setSubmissionsError(
          mapApiError(
            submissionsResult.reason,
            'Could not load assignment submissions.'
          )
        )
      }

      if (
        assignmentResult.status === 'rejected' &&
        submissionsResult.status === 'rejected'
      ) {
        setPageError('Unable to load assignment or submissions for this ID.')
      }

      setLoadingAssignmentData(false)
    }

    loadData()
  }, [assignmentId])

  async function handleQueueRun() {
    if (!assignmentId) return

    setQueueLoading(true)
    setQueueError(null)
    setStatusError(null)
    setIsPolling(false)

    try {
      const createdRun = await queueAnalysisRun(assignmentId)
      setCurrentRun(createdRun)
      setRunStatus({
        runId: createdRun.runId,
        assignmentId,
        status: createdRun.status,
        algorithmVersion: createdRun.algorithmVersion,
        createdAt: null,
        startedAt: null,
        finishedAt: null,
        errorMessage: null,
      })
    } catch (error) {
      setQueueError(mapApiError(error, 'Could not queue analysis run.'))
    } finally {
      setQueueLoading(false)
    }
  }

  return (
    <div className="h-screen flex">
      <Sidebar />
      <main className="ml-55 flex-1 overflow-y-auto bg-gray-50">
        <div className="max-w-4xl mx-auto p-6 space-y-6">

          <ErrorBanner message={pageError} />

          {/* Assignment Details */}
          <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-base font-bold text-gray-900 mb-4">Assignment Details</h2>

            {loadingAssignmentData && <LoadingSpinner message="Loading assignment…" />}
            <ErrorBanner message={assignmentError} />

            {!loadingAssignmentData && !assignmentError && !assignment && (
              <p className="text-sm text-gray-400">Enter an assignment ID to view details.</p>
            )}

            {assignment && (
              <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
                {[
                  ['Title',            assignment.title],
                  ['Language',         assignment.language],
                  ['Assignment Key',   assignment.assignmentKey],
                  ['Open',             assignment.isOpen ? 'Yes' : 'No'],
                  ['Due Date',         formatDate(assignment.dueDate)],
                  ['Key Expiry',       formatDate(assignment.keyExpiry)],
                  ['Auto Analysis',    assignment.autoAnalysis ? 'Yes' : 'No'],
                  ['Allow Late',       assignment.allowLate ? 'Yes' : 'No'],
                  ['Exclusion Code',   assignment.exclusionCode || 'N/A'],
                  ['Created',          formatDate(assignment.createdAt)],
                ].map(([label, value]) => (
                  <div key={label} className="flex flex-col gap-0.5">
                    <dt className="text-xs text-gray-400 uppercase tracking-wide">{label}</dt>
                    <dd className="text-gray-800 font-medium">{value}</dd>
                  </div>
                ))}
              </dl>
            )}
          </section>

          {/* Submissions */}
          <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-base font-bold text-gray-900 mb-4">Submissions</h2>

            <ErrorBanner message={submissionsError} />

            {!submissionsError && hasLoadedAssignment && submissions.length === 0 && (
              <EmptyState message="No submissions yet." detail="Students submit using the assignment key." />
            )}

            {submissions.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-gray-200 text-left text-xs text-gray-400 uppercase tracking-wide">
                      <th className="pb-3 pr-4">Submission ID</th>
                      <th className="pb-3 pr-4">Student ID</th>
                      <th className="pb-3 pr-4">Name</th>
                      <th className="pb-3 pr-4">Submitted At</th>
                      <th className="pb-3 pr-4">Files</th>
                      <th className="pb-3">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {submissions.map((s) => (
                      <tr key={s.submissionId} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 pr-4 font-mono text-xs text-gray-500">{s.submissionId.slice(-8)}</td>
                        <td className="py-3 pr-4 text-gray-700">{s.studentIdentifier}</td>
                        <td className="py-3 pr-4 text-gray-700">{s.studentName || '—'}</td>
                        <td className="py-3 pr-4 text-gray-500">{formatDate(s.submittedAt)}</td>
                        <td className="py-3 pr-4 text-gray-700">{s.fileCount}</td>
                        <td className="py-3"><StatusBadge status={s.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* Analysis Run */}
          <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-base font-bold text-gray-900 mb-4">Analysis Run</h2>

            <div className="flex flex-wrap gap-2 mb-4">
              <Button
                onClick={handleQueueRun}
                disabled={!hasLoadedAssignment || queueLoading}
              >
                {queueLoading ? 'Queueing…' : 'Run Analysis'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => refreshRunStatus()}
                disabled={!hasRun || statusLoading}
              >
                {statusLoading ? 'Refreshing…' : 'Refresh Status'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => setIsPolling((c) => !c)}
                disabled={!hasRun || terminalRunState}
              >
                {isPolling ? 'Stop Auto-Refresh' : 'Start Auto-Refresh'}
              </Button>
            </div>

            <ErrorBanner message={queueError} />
            <ErrorBanner message={statusError} />

            {!hasRun && (
              <p className="text-sm text-gray-400 mt-2">Queue a run to start monitoring analysis status.</p>
            )}

            {currentRun && (
              <div className="mt-4 border border-gray-100 rounded-xl overflow-hidden">
                <dl className="divide-y divide-gray-100 text-sm">
                  {[
                    ['Run ID',             <span className="font-mono text-gray-600">{currentRun.runId}</span>],
                    ['Algorithm Version',  runStatus?.algorithmVersion || currentRun.algorithmVersion],
                    ['Status',             <StatusBadge status={runStatus?.status || currentRun.status} />],
                    ['Created',            formatDate(runStatus?.createdAt)],
                    ['Started',            formatDate(runStatus?.startedAt)],
                    ['Finished',           formatDate(runStatus?.finishedAt)],
                  ].map(([label, value]) => (
                    <div key={label} className="flex items-center gap-4 px-4 py-3">
                      <dt className="w-40 text-xs text-gray-400 uppercase tracking-wide flex-shrink-0">{label}</dt>
                      <dd className="text-gray-800">{value}</dd>
                    </div>
                  ))}
                  {runStatus?.errorMessage && (
                    <div className="px-4 py-3">
                      <ErrorBanner message={`Failure: ${runStatus.errorMessage}`} />
                    </div>
                  )}
                </dl>
                {isPolling && !terminalRunState && (
                  <div className="px-4 py-2 bg-blue-50 border-t border-blue-100 text-xs text-blue-600 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                    Polling run status every 3 seconds…
                  </div>
                )}
              </div>
            )}

            {runStatus?.status === 'completed' && currentRun?.runId && (
              <div className="mt-4">
                <Button
                  variant="success"
                  onClick={() => navigate(`/similarity/${currentRun.runId}`)}
                >
                  View Similarity Results
                </Button>
              </div>
            )}
          </section>

        </div>
      </main>
    </div>
  )
}
