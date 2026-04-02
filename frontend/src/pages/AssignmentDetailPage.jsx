import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  downloadSubmissionsZip,
  getAnalysisRunStatus,
  getAssignmentSubmissions,
  getInstructorAssignmentById,
  importRepositoryZip,
  queueAnalysisRun,
  updateInstructorAssignment,
} from '../services/api'
import Sidebar from '../components/Sidebar/Sidebar'
import Button from '../components/ui/Button'
import { StatusBadge } from '../components/ui/Badge'
import ErrorBanner from '../components/ui/ErrorBanner'
import WarningBanner from '../components/ui/WarningBanner'
import {
  ArrowLeft, Copy, CheckCircle, Play, RefreshCw, Eye,
  Loader2, FileCode, Users, Clock, Key, Code2, Calendar,
  ToggleLeft, ToggleRight, ChevronRight, AlertTriangle,
  FlaskConical, Download, Upload,
} from 'lucide-react'

function mapApiError(error, fallback) {
  const message = error?.message || ''
  const normalized = message.toLowerCase()
  if (normalized.includes('401') || normalized.includes('unauthorized'))
    return 'Your session is missing or expired. Log in again and retry.'
  if (normalized.includes('403') || normalized.includes('not your assignment'))
    return 'You do not have permission to access this assignment.'
  if (normalized.includes('404') && normalized.includes('analysis run'))
    return 'Analysis run not found. Queue a new run or check the run ID.'
  if (normalized.includes('404') || normalized.includes('assignment not found'))
    return 'Assignment not found. Check the assignment ID and try again.'
  return message || fallback
}

function formatDate(value) {
  if (!value) return 'N/A'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

function getDateInputValue(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  const pad = (num) => String(num).padStart(2, '0')
  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hours = pad(date.getHours())
  const minutes = pad(date.getMinutes())

  return `${year}-${month}-${day}T${hours}:${minutes}`
}

function isOverdue(value) {
  if (!value) return false
  const d = new Date(value)
  return !Number.isNaN(d.getTime()) && d < new Date()
}

function truncateId(value) {
  if (!value) return value
  return value.length > 16 ? value.slice(0, 8) + '…' : value
}

export default function AssignmentDetailPage() {
  const { assignmentId, courseId } = useParams()
  const navigate = useNavigate()

  const [assignment, setAssignment]               = useState(null)
  const [submissions, setSubmissions]             = useState([])
  const [loadingAssignmentData, setLoading]       = useState(false)
  const [assignmentError, setAssignmentError]     = useState(null)
  const [submissionsError, setSubmissionsError]   = useState(null)
  const [pageError, setPageError]                 = useState(null)
  const [queueLoading, setQueueLoading]           = useState(false)
  const [queueError, setQueueError]               = useState(null)
  const [currentRun, setCurrentRun]               = useState(null)
  const [runStatus, setRunStatus]                 = useState(null)
  const [statusLoading, setStatusLoading]         = useState(false)
  const [statusError, setStatusError]             = useState(null)
  const [isPolling, setIsPolling]                 = useState(false)
  const [isExclusionExpanded, setIsExclusionExpanded] = useState(false)
  const [isEditing, setIsEditing]                 = useState(false)
  const [draftDueDate, setDraftDueDate]           = useState('')
  const [draftAllowLate, setDraftAllowLate]       = useState(false)
  const [draftAutoAnalysis, setDraftAutoAnalysis] = useState(false)
  const [draftExclusionCode, setDraftExclusionCode] = useState('')
  const [saveLoading, setSaveLoading]             = useState(false)
  const [saveError, setSaveError]                 = useState(null)
  const [copied, setCopied]                       = useState(false)
  const [exportLoading, setExportLoading]           = useState(false)
  const [exportError, setExportError]               = useState(null)
  const [importFile, setImportFile]                 = useState(null)
  const [importLoading, setImportLoading]           = useState(false)
  const [importError, setImportError]               = useState(null)
  const [importResult, setImportResult]             = useState(null)

  const hasLoadedAssignment = Boolean(assignment?.id)
  const hasRun              = Boolean(currentRun?.runId)
  const terminalRunState    = runStatus?.status === 'completed' || runStatus?.status === 'failed'
  const backPath            = courseId ? `/course/${courseId}` : '/dashboard'

  const refreshRunStatus = useCallback(async ({ silent = false } = {}) => {
    if (!currentRun?.runId) return
    if (!silent) setStatusLoading(true)
    setStatusError(null)
    try {
      const latest = await getAnalysisRunStatus(currentRun.runId)
      setRunStatus(latest)
    } catch (error) {
      setStatusError(mapApiError(error, 'Could not refresh analysis run status.'))
    } finally {
      if (!silent) setStatusLoading(false)
    }
  }, [currentRun?.runId])

  useEffect(() => {
    if (!isPolling || !currentRun?.runId || terminalRunState) return
    const timer = setInterval(() => refreshRunStatus({ silent: true }), 3000)
    return () => clearInterval(timer)
  }, [currentRun?.runId, isPolling, refreshRunStatus, terminalRunState])

  useEffect(() => {
    if (terminalRunState) setIsPolling(false)
  }, [terminalRunState])

  useEffect(() => {
    if (!assignmentId) return
    setLoading(true)
    setPageError(null); setAssignmentError(null); setSubmissionsError(null)
    setQueueError(null); setStatusError(null)
    setCurrentRun(null); setRunStatus(null); setIsPolling(false)

    const loadData = async () => {
      const [aRes, sRes] = await Promise.allSettled([
        getInstructorAssignmentById(assignmentId),
        getAssignmentSubmissions(assignmentId),
      ])
      if (aRes.status === 'fulfilled') {
        setAssignment(aRes.value)
      } else {
        setAssignment(null)
        setAssignmentError(mapApiError(aRes.reason, 'Could not load assignment details.'))
      }
      if (sRes.status === 'fulfilled') {
        setSubmissions(sRes.value)
      } else {
        setSubmissions([])
        setSubmissionsError(mapApiError(sRes.reason, 'Could not load submissions.'))
      }
      if (aRes.status === 'rejected' && sRes.status === 'rejected')
        setPageError('Unable to load assignment or submissions for this ID.')
      setLoading(false)
    }
    loadData()
  }, [assignmentId])

  async function handleQueueRun() {
    if (!assignmentId) return
    setQueueLoading(true); setQueueError(null); setStatusError(null); setIsPolling(false)
    try {
      const createdRun = await queueAnalysisRun(assignmentId)
      setCurrentRun(createdRun)
      setRunStatus({
        runId: createdRun.runId, assignmentId,
        status: createdRun.status,
        algorithmVersion: createdRun.algorithmVersion,
        createdAt: null, startedAt: null, finishedAt: null, errorMessage: null,
      })
      setIsPolling(true)
    } catch (error) {
      setQueueError(mapApiError(error, 'Could not queue analysis run.'))
    } finally {
      setQueueLoading(false)
    }
  }

  function handleCopyKey() {
    if (assignment?.assignmentKey) {
      navigator.clipboard.writeText(assignment.assignmentKey)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

<<<<<<< HEAD
=======
  async function handleExportSubmissions() {
    if (!assignmentId) return
    setExportLoading(true); setExportError(null)
    try {
      await downloadSubmissionsZip(assignmentId)
    } catch (error) {
      setExportError(mapApiError(error, 'Could not download submissions.'))
    } finally {
      setExportLoading(false)
    }
  }

  async function handleImportRepository() {
    if (!assignmentId || !importFile) return
    setImportLoading(true); setImportError(null); setImportResult(null)
    try {
      const result = await importRepositoryZip(assignmentId, importFile)
      setImportResult(result)
      setImportFile(null)
      // Refresh submissions list to show newly imported entries
      const fresh = await getAssignmentSubmissions(assignmentId).catch(() => [])
      setSubmissions(fresh)
    } catch (error) {
      setImportError(mapApiError(error, 'Could not import repository.'))
    } finally {
      setImportLoading(false)
    }
  }

>>>>>>> 151127fefb4fb9c591724bc54dc49de9c8fca4c8
  useEffect(() => {
    if (!assignment || isEditing) return
    setDraftDueDate(getDateInputValue(assignment.dueDate))
    setDraftAllowLate(Boolean(assignment.allowLate))
    setDraftAutoAnalysis(Boolean(assignment.autoAnalysis))
    setDraftExclusionCode(assignment.exclusionCode || '')
    setSaveError(null)
  }, [assignment, isEditing])

  function startEdit() {
    if (!assignment) return
    setDraftDueDate(getDateInputValue(assignment.dueDate))
    setDraftAllowLate(Boolean(assignment.allowLate))
    setDraftAutoAnalysis(Boolean(assignment.autoAnalysis))
    setDraftExclusionCode(assignment.exclusionCode || '')
    setSaveError(null)
    setIsEditing(true)
  }

  function cancelEdit() {
    setIsEditing(false)
    setSaveError(null)
  }

  async function handleSave() {
    if (!assignment) return
    setSaveLoading(true)
    setSaveError(null)

    const body = {
      dueDate: draftDueDate || null,
      allowLate: draftAllowLate,
      autoAnalysis: draftAutoAnalysis,
      exclusionCode: draftExclusionCode.trim() || null,
    }

    try {
      const updated = await updateInstructorAssignment(assignment.id, body)
      setAssignment(updated)
      setIsEditing(false)
    } catch (error) {
      setSaveError(mapApiError(error, 'Could not save assignment details.'))
    } finally {
      setSaveLoading(false)
    }
  }

  const assignmentDueDate = isEditing ? draftDueDate || null : assignment?.dueDate
  const overdue = isOverdue(assignmentDueDate)

  return (
    <div className="h-screen flex">
      <Sidebar />
      <main className="ml-55 flex-1 overflow-y-auto bg-brand-pink/40">
        <div className="mx-auto max-w-5xl p-6 lg:p-8">

          {/* ── Page header ── */}
          <div className="mb-7">
            <Link
              to={backPath}
              className="mb-4 inline-flex items-center gap-1.5 text-sm text-gray-400 no-underline transition-colors hover:text-brand-purple"
            >
              <ArrowLeft className="h-3.5 w-3.5" /> Back to Assignments
            </Link>

            {assignment && (
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-brand-purple/60">
                    Assignment
                  </p>
                  <h1 className="text-2xl font-bold text-gray-900">{assignment.title}</h1>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {assignment.language && (
                    <span className="rounded-full bg-orange-100 px-2.5 py-0.5 text-xs font-semibold text-orange-700">
                      {assignment.language.toUpperCase()}
                    </span>
                  )}
                  <StatusBadge status={assignment.isOpen ? 'open' : 'closed'} />
                </div>
              </div>
            )}
          </div>

          <ErrorBanner message={pageError} />

          {loadingAssignmentData && (
            <div className="flex items-center justify-center gap-2 py-24 text-sm text-gray-400">
              <Loader2 className="h-5 w-5 animate-spin" /> Loading assignment…
            </div>
          )}

          {!loadingAssignmentData && (
            <div className="space-y-5">

              {/* ── Assignment Details ── */}
              {(assignment || assignmentError) && (
                <section className="rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden">
                  <div className="border-b border-gray-100 bg-gray-50/60 px-6 py-3.5 flex items-center justify-between gap-3">
                    <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-400">
                      Assignment Details
                    </h2>
                    {assignment && (
                      <Button
                        variant={isEditing ? 'secondary' : 'ghost'}
                        size="sm"
                        onClick={isEditing ? cancelEdit : startEdit}
                      >
                        {isEditing ? 'Cancel edit' : 'Edit'}
                      </Button>
                    )}
                  </div>

                  <div className="p-6">
                    <ErrorBanner message={assignmentError} />

                    {assignment && (
                      <>
                        {/* Key + Due date — highlighted row */}
                        <div className="mb-5 grid gap-3 sm:grid-cols-2">
                          {/* Assignment key */}
                          <div className="rounded-xl border border-brand-purple/20 bg-brand-purple/5 p-4">
                            <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-brand-purple/60">
                              <Key className="h-3 w-3" /> Assignment Key
                            </div>
                            <div className="flex items-center gap-2">
                              <code className="flex-1 truncate rounded-lg bg-white px-2.5 py-1.5 text-sm font-mono font-semibold text-gray-800 shadow-sm border border-gray-100">
                                {assignment.assignmentKey || '—'}
                              </code>
                              <button
                                onClick={handleCopyKey}
                                className="rounded-lg p-1.5 text-brand-purple/60 transition-colors hover:bg-brand-purple/10 hover:text-brand-purple"
                                aria-label="Copy assignment key"
                              >
                                {copied
                                  ? <CheckCircle className="h-4 w-4 text-green-500" />
                                  : <Copy className="h-4 w-4" />}
                              </button>
                            </div>
                            <p className="mt-1.5 text-[11px] text-brand-purple/50">
                              Share this key with students to collect submissions
                            </p>
                          </div>

                          {/* Due date */}
                          <div className="rounded-xl border border-gray-200 bg-white p-4">
                            <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-gray-400">
                              <Calendar className="h-3 w-3" /> Due Date
                            </div>
                            {isEditing ? (
                              <input
                                type="datetime-local"
                                value={draftDueDate}
                                onChange={(e) => setDraftDueDate(e.target.value)}
                                className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 focus:border-brand-purple focus:outline-none focus:ring-2 focus:ring-brand-purple/20"
                              />
                            ) : (
                              <p className="text-sm font-semibold text-gray-800">
                                {formatDate(assignment.dueDate)}
                              </p>
                            )}
                            {overdue && (
                              <p className="mt-1 flex items-center gap-1 text-[11px] text-[#fb2c36CC]">
                                <AlertTriangle className="h-3 w-3" />
                                This assignment is past due
                              </p>
                            )}
                          </div>
                        </div>

                        {/* Secondary meta grid */}
                        <div className="grid gap-3 sm:grid-cols-3">
                          <MetaCard icon={Code2} label="Language" value={assignment.language?.toUpperCase()} />

                          <div className="rounded-xl border border-gray-200 bg-white p-4">
                            <div className="mb-1.5 flex items-center gap-1.5 text-xs text-gray-400 uppercase tracking-wide">
                              <ToggleLeft className="h-3 w-3" /> Allow Lates
                            </div>
                            {isEditing ? (
                              <div className="inline-flex overflow-hidden rounded-xl border border-gray-200 bg-white text-sm shadow-sm">
                                <button
                                  type="button"
                                  onClick={() => setDraftAllowLate(true)}
                                  className={`px-3 py-1.5 ${draftAllowLate ? 'bg-brand-purple text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                                >Yes</button>
                                <button
                                  type="button"
                                  onClick={() => setDraftAllowLate(false)}
                                  className={`px-3 py-1.5 ${!draftAllowLate ? 'bg-brand-purple text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                                >No</button>
                              </div>
                            ) : (
                              <p className="text-sm font-medium text-gray-800">
                                {assignment.allowLate ? 'Yes' : 'No'}
                              </p>
                            )}
                          </div>

                          <div className="rounded-xl border border-gray-200 bg-white p-4">
                            <div className="mb-1.5 flex items-center gap-1.5 text-xs text-gray-400 uppercase tracking-wide">
                              <ToggleLeft className="h-3 w-3" />
                              Auto Analysis
                            </div>
                            {isEditing ? (
                              <div className="inline-flex overflow-hidden rounded-xl border border-gray-200 bg-white text-sm shadow-sm">
                                <button
                                  type="button"
                                  onClick={() => setDraftAutoAnalysis(true)}
                                  className={`px-3 py-1.5 ${draftAutoAnalysis ? 'bg-brand-purple text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                                >Yes</button>
                                <button
                                  type="button"
                                  onClick={() => setDraftAutoAnalysis(false)}
                                  className={`px-3 py-1.5 ${!draftAutoAnalysis ? 'bg-brand-purple text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                                >No</button>
                              </div>
                            ) : (
                              <p className="text-sm font-medium text-gray-800">
                                {assignment.autoAnalysis ? 'Yes' : 'No'}
                              </p>
                            )}
                          </div>

                          <MetaCard icon={Clock} label="Created" value={formatDate(assignment.createdAt)} />
                        </div>

                        {/* Exclusion code */}
                        <div className="mt-4 rounded-xl border border-gray-200 bg-white p-4">
                          <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                            <div className="flex items-center gap-1.5 text-xs text-gray-400 uppercase tracking-wide">
                              <FileCode className="h-3 w-3" /> Exclusion Code
                            </div>
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => setIsExclusionExpanded(prev => !prev)}
                              className="self-start sm:self-auto"
                            >
                              {isExclusionExpanded ? 'Collapse' : 'Expand'}
                            </Button>
                          </div>
                          {isEditing ? (
                            <textarea
                              value={draftExclusionCode}
                              onChange={(e) => setDraftExclusionCode(e.target.value)}
                              rows={isExclusionExpanded ? 10 : 4}
                              className={`w-full resize-y rounded-lg border border-gray-200 bg-gray-50 p-3 text-xs font-mono text-gray-700 transition-all focus:border-brand-purple focus:outline-none focus:ring-2 focus:ring-brand-purple/10 ${isExclusionExpanded ? 'max-h-96' : 'max-h-40'}`}
                            />
                          ) : (
                            <pre className={`overflow-auto whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-xs font-mono text-gray-700 transition-all ${isExclusionExpanded ? 'max-h-96' : 'max-h-20'}`}>
                              {assignment.exclusionCode ? assignment.exclusionCode : 'N/A'}
                            </pre>
                          )}
                        </div>

                        {isEditing && (
                          <>
                            <ErrorBanner message={saveError} />
                            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-end">
                              <Button
                                variant="secondary"
                                onClick={cancelEdit}
                                disabled={saveLoading}
                              >
                                Cancel
                              </Button>
                              <Button
                                onClick={handleSave}
                                disabled={saveLoading}
                              >
                                {saveLoading
                                  ? <><Loader2 className="h-4 w-4 animate-spin" /> Saving…</>
                                  : 'Save changes'}
                              </Button>
                            </div>
                          </>
                        )}
                      </>
                    )}
                  </div>
                </section>
              )}

              {/* ── Step 1: Submissions ── */}
              <section className="rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden">
                <div className="border-b border-gray-100 bg-gray-50/60 px-6 py-3.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-purple text-[10px] font-bold text-white">1</span>
                      <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-500">
                        Review Submissions
                      </h2>
                    </div>
                    {hasLoadedAssignment && (
                      <div className="flex items-center gap-2">
                        <span className="rounded-full bg-brand-purple/10 px-2.5 py-0.5 text-xs font-semibold text-brand-purple">
                          {submissions.length} submission{submissions.length !== 1 ? 's' : ''}
                        </span>
                        {submissions.length > 0 && (
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={handleExportSubmissions}
                            disabled={exportLoading}
                          >
                            {exportLoading
                              ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
                              : <Download className="h-3.5 w-3.5" />}
                            {exportLoading ? 'Exporting…' : 'Export ZIP'}
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                <div className="p-6">
                  <ErrorBanner message={submissionsError} />
                  <ErrorBanner message={exportError} />

                  {!submissionsError && hasLoadedAssignment && submissions.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-purple/10">
                        <Users className="h-6 w-6 text-brand-purple/50" />
                      </div>
                      <p className="text-sm font-semibold text-gray-600">No submissions yet</p>
                      <p className="mt-1 text-xs text-gray-400">
                        Students submit using the assignment key above.
                      </p>
                    </div>
                  )}

                  {submissions.length > 0 && (
                    <div className="overflow-x-auto rounded-xl border border-gray-100">
                      <table className="w-full text-sm">
                        <thead className="w-full table table-fixed">
                          <tr className="border-b border-gray-100 bg-gray-50/80 text-left text-xs text-gray-400 uppercase tracking-wide">
                            <th className="px-5 py-3">Student</th>
                            <th className="px-4 py-3">Submitted</th>
                            <th className="px-4 py-3">Files</th>
                            <th className="px-4 py-3">Status</th>
                            <th className="px-4 py-3 text-right text-[11px] font-normal text-gray-300">
                              ID
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 max-h-60 w-full overflow-y-scroll block">
                          {submissions.map((s) => (
                            <tr
                              key={s.submissionId}
                              className="transition-colors w-full table table-fixed"
                            >
                              <td className="px-5 py-4">
                                <p className="font-semibold text-gray-900">
                                  {truncateId(s.studentName) || <span className="font-normal italic text-gray-400">Unnamed</span>}
                                </p>
                                <p className="mt-0.5 font-mono text-xs text-gray-400" title={s.studentIdentifier}>{truncateId(s.studentIdentifier)}</p>
                              </td>
                              <td className="px-4 py-4 text-sm text-gray-500">{formatDate(s.submittedAt)}</td>
                              <td className="px-4 py-4 text-sm text-gray-700">{s.fileCount}</td>
                              <td className="px-4 py-4"><StatusBadge status={s.status} /></td>
                              <td className="px-4 py-4 text-right font-mono text-xs text-gray-300">
                                {s.submissionId?.slice(-8)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {/* ── Import Repository ── */}
                  {hasLoadedAssignment && (
                    <div className="mt-5 rounded-xl border border-dashed border-gray-300 bg-gray-50/50 p-5">
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <p className="text-sm font-semibold text-gray-700">
                            <Upload className="mr-1.5 inline h-4 w-4 text-gray-400" />
                            Import Submissions
                          </p>
                          <p className="mt-0.5 text-xs text-gray-400">
                            Bulk-add submissions from another system. Upload a <code className="rounded bg-gray-200 px-1">.zip</code> file exported from Token Trail or structured the same way.
                          </p>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <label className="inline-flex cursor-pointer items-center gap-1.5 rounded-xl border border-gray-300 bg-white px-3 py-1.5 text-xs font-semibold text-gray-600 shadow-sm transition-colors hover:bg-gray-50">
                            <FileCode className="h-3.5 w-3.5" />
                            {importFile ? importFile.name : 'Choose ZIP…'}
                            <input
                              type="file"
                              accept=".zip"
                              className="hidden"
                              onChange={(e) => {
                                setImportFile(e.target.files?.[0] || null)
                                setImportResult(null); setImportError(null)
                              }}
                            />
                          </label>
                          <Button
                            size="sm"
                            onClick={handleImportRepository}
                            disabled={!importFile || importLoading}
                          >
                            {importLoading
                              ? <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Importing…</>
                              : <><Upload className="h-3.5 w-3.5" /> Import</>}
                          </Button>
                        </div>
                      </div>

                      <ErrorBanner message={importError} />

                      {importResult && (
                        <div className="mt-3 rounded-xl border border-gray-200 bg-white p-4">
                          <div className="flex items-center gap-3 mb-2">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <p className="text-sm font-semibold text-gray-800">
                              Import complete — {importResult.imported} imported, {importResult.skipped} skipped
                            </p>
                          </div>

                          {importResult.details?.length > 0 && (
                            <div className="mb-2">
                              <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-400 mb-1">Imported</p>
                              <div className="space-y-0.5">
                                {importResult.details.map((d) => (
                                  <p key={d.submissionId} className="text-xs text-gray-600">
                                    <span className="font-medium">{d.folder}</span>
                                    <span className="text-gray-400"> — {d.fileCount} file{d.fileCount !== 1 ? 's' : ''}</span>
                                  </p>
                                ))}
                              </div>
                            </div>
                          )}

                          {importResult.skippedDetails?.length > 0 && (
                            <div>
                              <p className="text-[11px] font-semibold uppercase tracking-wide text-amber-500 mb-1">Skipped</p>
                              <div className="space-y-0.5">
                                {importResult.skippedDetails.map((s, i) => (
                                  <p key={i} className="text-xs text-amber-700">
                                    <span className="font-medium">{s.folder}</span>
                                    <span className="text-amber-500"> — {s.reason}</span>
                                  </p>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </section>

              {/* ── Step 2: Run Analysis ── */}
              {hasLoadedAssignment && (
                <section className="rounded-2xl border border-brand-purple/20 bg-gradient-to-br from-brand-purple/[0.04] to-transparent shadow-sm overflow-hidden">
                  <div className="border-b border-brand-purple/10 px-6 py-3.5">
                    <div className="flex items-center gap-2.5">
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-purple text-[10px] font-bold text-white">2</span>
                      <h2 className="text-xs font-semibold uppercase tracking-widest text-brand-purple/60">
                        Run Similarity Analysis
                      </h2>
                    </div>
                  </div>

                  <div className="p-6">
                    {/* CTA area */}
                    <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm font-semibold text-gray-800">
                          Analyze submissions for code similarity
                        </p>
                        <p className="mt-0.5 text-xs text-gray-500">
                          {submissions.length > 0
                            ? `Compare all ${submissions.length} submission${submissions.length !== 1 ? 's' : ''} and detect structural overlap patterns.`
                            : 'Collect submissions before running analysis.'}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <Button
                          size="lg"
                          onClick={handleQueueRun}
                          disabled={!hasLoadedAssignment || queueLoading || submissions.length === 0}
                        >
                          {queueLoading
                            ? <><Loader2 className="h-4 w-4 animate-spin" /> Queueing…</>
                            : <><FlaskConical className="h-4 w-4" /> Run Similarity Analysis</>}
                        </Button>
                        {hasRun && (
                          <Button
                            variant="secondary"
                            onClick={() => refreshRunStatus()}
                            disabled={statusLoading}
                            size="lg"
                          >
                            {statusLoading
                              ? <Loader2 className="h-4 w-4 animate-spin" />
                              : <RefreshCw className="h-4 w-4" />}
                          </Button>
                        )}
                      </div>
                    </div>

                    <ErrorBanner message={queueError} />
                    <ErrorBanner message={statusError} />

                    {!hasRun && (
                      <p className="text-xs text-gray-400">
                        No analysis has been run yet for this assignment.
                      </p>
                    )}

                    {/* Run status card */}
                    {currentRun && (
                      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
                        <div className="grid grid-cols-2 divide-x divide-gray-100 border-b border-gray-100 sm:grid-cols-4">
                          {[
                            ['Status',    <StatusBadge status={runStatus?.status || currentRun.status} />],
                            ['Algorithm', runStatus?.algorithmVersion || currentRun.algorithmVersion || '—'],
                            ['Started',   formatDate(runStatus?.startedAt)],
                            ['Finished',  formatDate(runStatus?.finishedAt)],
                          ].map(([label, val]) => (
                            <div key={label} className="px-4 py-3">
                              <p className="text-[10px] font-semibold uppercase tracking-wide text-gray-400">{label}</p>
                              <div className="mt-1 text-sm text-gray-700">{val}</div>
                            </div>
                          ))}
                        </div>

                        <div className="flex items-center justify-between px-4 py-2.5">
                          <span className="font-mono text-xs text-gray-400">
                            Run ID: {currentRun.runId}
                          </span>
                          <label className="flex cursor-pointer items-center gap-1.5 text-xs text-gray-500 select-none">
                            <input
                              type="checkbox"
                              checked={isPolling}
                              onChange={() => { if (!terminalRunState) setIsPolling(c => !c) }}
                              disabled={terminalRunState}
                              className="rounded accent-brand-purple"
                            />
                            <RefreshCw className="h-3 w-3" /> Auto-refresh
                          </label>
                        </div>

                        {isPolling && !terminalRunState && (
                          <div className="flex items-center gap-1.5 border-t border-blue-100 bg-blue-50 px-4 py-2 text-xs text-blue-600">
                            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-500" />
                            Polling every 3 seconds…
                          </div>
                        )}

                        {runStatus?.errorMessage && (
                          <div className="border-t border-gray-100 px-4 py-3">
                            <ErrorBanner message={`Failure: ${runStatus.errorMessage}`} />
                          </div>
                        )}

                        {runStatus?.warnings?.length > 0 && (
                          <div className="border-t border-gray-100 px-4 py-3">
                            <WarningBanner warnings={runStatus.warnings} />
                          </div>
                        )}

                        {runStatus?.pairsAnalyzed != null && (
                          <div className="flex items-center gap-4 border-t border-gray-100 px-4 py-2.5 text-xs text-gray-500">
                            <span>
                              <span className="font-semibold text-gray-700">{runStatus.pairsAnalyzed}</span> pair{runStatus.pairsAnalyzed !== 1 ? 's' : ''} analyzed
                            </span>
                            {runStatus.pairsFailed > 0 && (
                              <span className="text-amber-600">
                                <span className="font-semibold">{runStatus.pairsFailed}</span> failed
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Step 3: View Results — shown when analysis is done */}
                    {runStatus?.status === 'completed' && currentRun?.runId && (
                      <div className="mt-4 flex items-center gap-4 rounded-xl border border-green-200 bg-green-50 px-5 py-4">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-green-100">
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-semibold text-green-800">Analysis complete</p>
                          <p className="text-xs text-green-600">
                            Similarity results are ready to review.
                          </p>
                        </div>
                        <Button
                          variant="success"
                          size="lg"
                          onClick={() => navigate(`/similarity/${currentRun.runId}`)}
                        >
                          <Eye className="h-4 w-4" /> View Results
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </div>
                </section>
              )}

            </div>
          )}
        </div>
      </main>
    </div>
  )
}


function MetaCard({ icon: Icon, label, value }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4">
      <div className="mb-1 flex items-center gap-1.5 text-xs text-gray-400 uppercase tracking-wide">
        {Icon && <Icon className="h-3 w-3" />}
        {label}
      </div>
      <p className="text-sm font-medium text-gray-800">{value ?? '—'}</p>
    </div>
  )
}
