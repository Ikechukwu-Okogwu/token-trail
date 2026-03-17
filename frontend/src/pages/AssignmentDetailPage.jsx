import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  getAnalysisRunStatus,
  getAssignmentSubmissions,
  getInstructorAssignmentById,
  queueAnalysisRun,
} from '../services/api'

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

function runStatusColor(status) {
  switch (status) {
    case 'queued':
      return '#c9a227'
    case 'running':
      return '#4ea1ff'
    case 'completed':
      return '#2db783'
    case 'failed':
      return '#ff6b6b'
    default:
      return '#9aa0a6'
  }
}

function isValidAssignmentId(value) {
  return /^[a-f0-9]{24}$/i.test(value || '')
}

export default function AssignmentDetailPage() {
  const { courseId, assignmentId: assignmentIdParam } = useParams()
  const [assignmentIdInput, setAssignmentIdInput] = useState(assignmentIdParam || '')
  const [assignmentId, setAssignmentId] = useState(assignmentIdParam || '')

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
  const resultsUrl =
    courseId && assignmentIdParam && currentRun?.runId
      ? `/course/${courseId}/assignment/${assignmentIdParam}/run/${currentRun.runId}/results`
      : null

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

  const runStatusBadge = useMemo(() => {
    if (!runStatus?.status) return null
    return {
      color: runStatusColor(runStatus.status),
      text: runStatus.status.toUpperCase(),
    }
  }, [runStatus?.status])

  const loadAssignmentData = useCallback(async (nextId) => {
    if (!nextId) {
      setPageError('Enter an assignment ID first.')
      return
    }

    setAssignmentId(nextId)
    setLoadingAssignmentData(true)
    setPageError(null)
    setAssignmentError(null)
    setSubmissionsError(null)
    setQueueError(null)
    setStatusError(null)
    setCurrentRun(null)
    setRunStatus(null)
    setIsPolling(false)

    const [assignmentResult, submissionsResult] = await Promise.allSettled([
      getInstructorAssignmentById(nextId),
      getAssignmentSubmissions(nextId),
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
  }, [])

  useEffect(() => {
    if (!assignmentIdParam) return
    setAssignmentIdInput(assignmentIdParam)
    if (!isValidAssignmentId(assignmentIdParam)) {
      setPageError(
        'Route assignment ID is not in API format. Enter a valid assignment ID and click Load.'
      )
      return
    }
    loadAssignmentData(assignmentIdParam)
  }, [assignmentIdParam, loadAssignmentData])

  async function handleLoadAssignment(event) {
    event.preventDefault()
    const nextId = assignmentIdInput.trim()
    await loadAssignmentData(nextId)
  }

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
    <div>
      <h2>Instructor Assignment Detail</h2>
      <p>Load assignment details, inspect submissions, and monitor analysis runs.</p>

      <form onSubmit={handleLoadAssignment} style={{ marginBottom: '1rem' }}>
        <label htmlFor="assignment-id-input">Assignment ID</label>
        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
          <input
            id="assignment-id-input"
            type="text"
            value={assignmentIdInput}
            onChange={(event) => setAssignmentIdInput(event.target.value)}
            placeholder="Enter assignment ID"
            style={{ flex: 1, padding: '0.5rem' }}
          />
          <button type="submit" disabled={loadingAssignmentData}>
            {loadingAssignmentData ? 'Loading...' : 'Load'}
          </button>
        </div>
      </form>

      {pageError && <p style={{ color: '#ff6b6b' }}>{pageError}</p>}

      <section style={{ marginBottom: '1.5rem' }}>
        <h3>Assignment Details</h3>
        {loadingAssignmentData && <p>Loading assignment data...</p>}
        {assignmentError && <p style={{ color: '#ff6b6b' }}>{assignmentError}</p>}
        {!loadingAssignmentData && !assignmentError && !assignment && (
          <p>Enter an assignment ID to view details.</p>
        )}
        {assignment && (
          <div style={{ background: '#67769c', borderRadius: 8, padding: '1rem' }}>
            <p>
              <strong>Title:</strong> {assignment.title}
            </p>
            <p>
              <strong>Language:</strong> {assignment.language}
            </p>
            <p>
              <strong>Assignment Key:</strong> {assignment.assignmentKey}
            </p>
            <p>
              <strong>Open:</strong> {assignment.isOpen ? 'Yes' : 'No'}
            </p>
            <p>
              <strong>Due Date:</strong> {formatDate(assignment.dueDate)}
            </p>
            <p>
              <strong>Key Expiry:</strong> {formatDate(assignment.keyExpiry)}
            </p>
            <p>
              <strong>Auto Analysis:</strong> {assignment.autoAnalysis ? 'Yes' : 'No'}
            </p>
            <p>
              <strong>Allow Late:</strong> {assignment.allowLate ? 'Yes' : 'No'}
            </p>
            <p>
              <strong>Exclusion Code:</strong> {assignment.exclusionCode || 'N/A'}
            </p>
            <p>
              <strong>Created:</strong> {formatDate(assignment.createdAt)}
            </p>
          </div>
        )}
      </section>

      <section style={{ marginBottom: '1.5rem' }}>
        <h3>Submissions</h3>
        {submissionsError && <p style={{ color: '#ff6b6b' }}>{submissionsError}</p>}
        {!submissionsError && hasLoadedAssignment && submissions.length === 0 && (
          <p>No submissions found for this assignment yet.</p>
        )}
        {submissions.length > 0 && (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th align="left">Submission ID</th>
                  <th align="left">Student Identifier</th>
                  <th align="left">Student Name</th>
                  <th align="left">Submitted At</th>
                  <th align="left">File Count</th>
                  <th align="left">Status</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((submission) => (
                  <tr key={submission.submissionId}>
                    <td>{submission.submissionId}</td>
                    <td>{submission.studentIdentifier}</td>
                    <td>{submission.studentName || 'N/A'}</td>
                    <td>{formatDate(submission.submittedAt)}</td>
                    <td>{submission.fileCount}</td>
                    <td>{submission.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section style={{ marginBottom: '1.5rem' }}>
        <h3>Analysis Run</h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={handleQueueRun}
            disabled={!hasLoadedAssignment || queueLoading}
          >
            {queueLoading ? 'Queueing...' : 'Run Analysis'}
          </button>
          <button
            type="button"
            onClick={() => refreshRunStatus()}
            disabled={!hasRun || statusLoading}
          >
            {statusLoading ? 'Refreshing...' : 'Refresh Status'}
          </button>
          <button
            type="button"
            onClick={() => setIsPolling((current) => !current)}
            disabled={!hasRun || terminalRunState}
          >
            {isPolling ? 'Stop Polling' : 'Start Polling'}
          </button>
        </div>

        {queueError && <p style={{ color: '#ff6b6b' }}>{queueError}</p>}
        {statusError && <p style={{ color: '#ff6b6b' }}>{statusError}</p>}

        {!hasRun && <p>Queue a run to start monitoring analysis status.</p>}
        {currentRun && (
          <div style={{ marginTop: '1rem', background: '#4cbdd1', borderRadius: 8, padding: '1rem' }}>
            <p>
              <strong>Run ID:</strong> {currentRun.runId}
            </p>
            <p>
              <strong>Algorithm Version:</strong> {runStatus?.algorithmVersion || currentRun.algorithmVersion}
            </p>
            <p>
              <strong>Status:</strong>{' '}
              <span
                style={{
                  color: runStatusBadge?.color || '#9aa0a6',
                  fontWeight: 700,
                }}
              >
                {runStatusBadge?.text || currentRun.status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </p>
            <p>
              <strong>Created:</strong> {formatDate(runStatus?.createdAt)}
            </p>
            <p>
              <strong>Started:</strong> {formatDate(runStatus?.startedAt)}
            </p>
            <p>
              <strong>Finished:</strong> {formatDate(runStatus?.finishedAt)}
            </p>
            {runStatus?.errorMessage && (
              <p style={{ color: '#ff6b6b' }}>
                <strong>Failure:</strong> {runStatus.errorMessage}
              </p>
            )}
            {isPolling && !terminalRunState && (
              <p style={{ color: '#4ea1ff' }}>Polling run status every 3 seconds.</p>
            )}
            {runStatus?.status === 'completed' && resultsUrl && (
              <p style={{ marginTop: '0.75rem' }}>
                <Link to={resultsUrl}>View Similarity Results</Link>
              </p>
            )}
          </div>
        )}
      </section>
    </div>
  )
}
