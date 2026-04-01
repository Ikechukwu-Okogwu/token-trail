import { useState, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { validateAssignmentKey, submitAssignment } from '../services/api'
import { FileText, KeyRound, Upload, CheckCircle, Loader2, ArrowRight, Info, X, RotateCcw, Home } from 'lucide-react'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import ErrorBanner from '../components/ui/ErrorBanner'

function formatDueDate(value) {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

const STEPS = ['Enter Key', 'Upload Code', 'Done']

export default function StudentSubmitPage() {
  const [step, setStep] = useState('key')

  const [studentId, setStudentId] = useState('')
  const [key, setKey] = useState('')
  const [keyLoading, setKeyLoading] = useState(false)
  const [keyError, setKeyError] = useState('')
  const [assignment, setAssignment] = useState(null)

  const [name, setName] = useState('')
  const [zipFile, setZipFile] = useState(null)
  const [uploadLoading, setUploadLoading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [dragOver, setDragOver] = useState(false)

  const [result, setResult] = useState(null)

  const fileRef = useRef(null)

  const currentIdx = step === 'key' ? 0 : step === 'upload' ? 1 : 2

  async function handleContinue(e) {
    e.preventDefault()
    setKeyError('')

    if (!studentId) { setKeyError('Please enter your Student ID.'); return }
    if (!key)       { setKeyError('Please enter your Assignment Key.'); return }

    setKeyLoading(true)
    try {
      const data = await validateAssignmentKey(key.trim())

      if (!data.valid || !data.assignment) {
        setKeyError('Assignment key not found. Check with your instructor!')
        return
      }

      if (!data.assignment.isOpen) {
        setKeyError('This assignment is closed and not accepting submissions.')
        return
      }
      if (data.assignment.dueDate && !data.assignment.allowLate) {
        const dueDate = new Date(data.assignment.dueDate)
        if (!Number.isNaN(dueDate.getTime()) && dueDate < new Date()) {
          setKeyError('This assignment is past the due date and no longer accepting submissions.')
          return
        }
      }

      setAssignment(data.assignment)
      setStep('upload')
    } catch (err) {
      setKeyError('Could not reach the server. Please try again.')
    } finally {
      setKeyLoading(false)
    }
  }

  function handleFileChange(e) {
    const file = e.target.files[0]
    if (!file) return
    if (!file.name.endsWith('.zip')) {
      setUploadError('Please select a .zip file.')
      return
    }
    setZipFile(file)
    setUploadError('')
  }

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f && (f.name.endsWith('.zip') || f.type === 'application/zip')) {
      setZipFile(f)
      setUploadError('')
    } else {
      setUploadError('Please upload a .zip file.')
    }
  }, [])

  async function handleUpload(e) {
    e.preventDefault()
    setUploadError('')

    if (!zipFile) {
      setUploadError('Please choose a ZIP file first.')
      return
    }
    setUploadLoading(true)
    try {
      const data = await submitAssignment({
        assignmentKey: key.trim(),
        studentIdentifier: studentId.trim(),
        studentName: name.trim() || undefined,
        zipFile: zipFile,
      })
      setResult(data)
      setStep('done')
    } catch (err) {
      if (err.status === 404) {
        setUploadError('Assignment key is no longer valid!')
      } else if (err.status === 400) {
        if ((err.message || '').toLowerCase().includes('due date')) {
          setUploadError('This assignment is past the due date and no longer accepting submissions.')
        } else {
          setUploadError(err.message || 'Something is wrong with your ZIP file.')
        }
      } else {
        setUploadError('Upload failed. Please try again.')
      }
    } finally {
      setUploadLoading(false)
    }
  }

  function startOver() {
    setStep('key')
    setStudentId(''); setKey(''); setKeyError(''); setAssignment(null)
    setName(''); setZipFile(null); setUploadError(''); setDragOver(false); setResult(null)
  }

  return (
    <div className="relative flex min-h-screen flex-col bg-[radial-gradient(circle_at_top,rgba(86,79,103,0.06),transparent_60%),_#FEF7FF66]">
      {/* Header band — compact, matching auth page */}
      <header className="relative bg-landing px-6 pb-12 pt-7">
        <div className="mx-auto flex max-w-lg flex-col items-center gap-2.5">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/15">
              <FileText className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-semibold text-white tracking-tight">Token Trail</span>
          </Link>
          <p className="text-sm font-medium text-white/80">
            Submit your assignment securely in a few quick steps
          </p>
        </div>
        <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-b from-transparent to-brand-pink/40" />
      </header>

      {/* Radial glow */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[500px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(ellipse_at_center,rgba(120,109,145,0.08),transparent_70%)]" />

      {/* Content */}
      <div className="relative z-10 flex flex-1 flex-col items-center px-4 pt-8 pb-12">
        <div className="w-full max-w-xl">
          {/* Step progress indicator */}
          <div className="mb-8 flex items-center justify-center">
            {STEPS.map((s, i) => (
              <div key={s} className="flex items-center">
                <div className="flex items-center gap-2.5">
                  <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold transition-all ${
                    i < currentIdx || (step === 'done' && i === currentIdx)
                      ? 'bg-brand-purple text-white shadow-sm'
                      : i === currentIdx
                        ? 'bg-brand-purple text-white shadow-md ring-4 ring-brand-purple/15'
                        : 'bg-gray-200 text-gray-500'
                  }`}>
                    {i < currentIdx || (step === 'done' && i === currentIdx) ? <CheckCircle className="h-4 w-4" /> : i + 1}
                  </div>
                  <span className={`text-sm ${
                    i <= currentIdx ? 'text-gray-900 font-semibold' : 'text-gray-500'
                  }`}>{s}</span>
                </div>
                {i < STEPS.length - 1 && (
                  <div className={`mx-5 h-px w-12 ${i < currentIdx || step === 'done' ? 'bg-brand-purple' : 'bg-gray-300'}`} />
                )}
              </div>
            ))}
          </div>

          {/* Card */}
          <div className="rounded-2xl border border-white/60 bg-white px-10 py-10 ring-1 ring-black/5 shadow-xl hover:shadow-2xl transition-shadow duration-300">

            {/* ── STEP 1: Student ID + Key ── */}
            {step === 'key' && (
              <form onSubmit={handleContinue} className="flex flex-col gap-5">
                <div className="text-center mb-2">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-purple/10">
                    <KeyRound className="h-6 w-6 text-brand-purple" />
                  </div>
                  <h2 className="mt-4 text-xl font-bold text-gray-900">Enter Assignment Key</h2>
                  <p className="mt-1.5 text-sm text-gray-500">Your instructor will provide this key</p>
                </div>
                <ErrorBanner message={keyError} />
                <Input
                  label="Student ID"
                  type="text"
                  value={studentId}
                  onChange={e => { setStudentId(e.target.value); setKeyError('') }}
                  placeholder="e.g. 5342145"
                  disabled={keyLoading}
                />
                <Input
                  label="Assignment Key"
                  type="text"
                  value={key}
                  onChange={e => { setKey(e.target.value); setKeyError('') }}
                  placeholder="e.g. ASSIGN-0234-ABC"
                  disabled={keyLoading}
                />
                <Button type="submit" fullWidth disabled={keyLoading} size="lg" className="mt-1">
                  {keyLoading
                    ? <><Loader2 className="h-4 w-4 animate-spin" /> Checking…</>
                    : <><ArrowRight className="h-4 w-4" /> Continue</>
                  }
                </Button>
              </form>
            )}

            {/* ── STEP 2: Upload ZIP ── */}
            {step === 'upload' && assignment && (
              <form onSubmit={handleUpload} className="flex flex-col gap-5">
                <div className="text-center mb-1">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-purple/10">
                    <Upload className="h-6 w-6 text-brand-purple" />
                  </div>
                  <h2 className="mt-4 text-xl font-bold text-gray-900">Upload Your Code</h2>
                  <p className="mt-1.5 text-sm text-gray-500">Upload your assignment files as a ZIP archive</p>
                  <div className="mt-2 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs text-gray-400">
                    <span>Key: <span className="font-mono text-gray-500">{key.trim()}</span></span>
                    {assignment.dueDate && (
                      <span>Due: <span className="font-medium text-gray-500">{formatDueDate(assignment.dueDate)}</span></span>
                    )}
                  </div>
                </div>

                <ErrorBanner message={uploadError} />

                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Student ID"
                    type="text"
                    value={studentId}
                    readOnly
                  />
                  <Input
                    label="Your Name (optional)"
                    type="text"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder="e.g. Jane Doe"
                    disabled={uploadLoading}
                  />
                </div>

                {/* Drop zone */}
                <div>
                  <label htmlFor="file-input" className="text-sm font-medium text-gray-700 mb-1.5 block">Code Upload</label>
                  {!zipFile ? (
                    <div
                      role="button"
                      tabIndex={0}
                      onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                      onDragLeave={() => setDragOver(false)}
                      onDrop={handleDrop}
                      onClick={() => fileRef.current.click()}
                      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') fileRef.current.click() }}
                      className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 transition-all cursor-pointer ${
                        dragOver
                          ? 'border-brand-purple bg-brand-purple/5 shadow-inner'
                          : 'border-gray-300 hover:border-brand-purple/40 hover:bg-brand-purple/[0.02]'
                      }`}
                    >
                      <div className={`flex h-11 w-11 items-center justify-center rounded-xl transition-colors ${
                        dragOver ? 'bg-brand-purple/15' : 'bg-gray-100'
                      }`}>
                        <Upload className={`h-5 w-5 transition-colors ${dragOver ? 'text-brand-purple' : 'text-gray-400'}`} />
                      </div>
                      <p className="mt-3 text-sm font-medium text-gray-700">
                        Drag & drop your .zip file here
                      </p>
                      <p className="mt-1 text-xs text-gray-400">or click to browse</p>
                      <p className="mt-3 text-xs text-gray-400">Supported format: .zip</p>
                    </div>
                  ) : (
                    <div className="flex items-center gap-3 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3.5">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-purple/10">
                        <FileText className="h-5 w-5 text-brand-purple" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-900">{zipFile.name}</p>
                        <p className="text-xs text-gray-400">{(zipFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); setZipFile(null); setUploadError('') }}
                        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-gray-200 hover:text-gray-600"
                        aria-label="Remove file"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                  <input
                    ref={fileRef}
                    id="file-input"
                    type="file"
                    accept=".zip"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </div>

                <Button type="submit" fullWidth disabled={uploadLoading || !zipFile} size="lg">
                  {uploadLoading
                    ? <><Loader2 className="h-4 w-4 animate-spin" /> Uploading…</>
                    : <><Upload className="h-4 w-4" /> Submit Assignment</>
                  }
                </Button>

                {/* Retention disclaimer */}
                <p className="flex items-start gap-2 rounded-xl bg-gray-50 border border-gray-100 p-3 text-xs text-gray-500">
                  <Info className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                  Submitted files are retained for 30 days for analysis purposes, then permanently deleted.
                </p>
              </form>
            )}

            {/* ── STEP 3: Success ── */}
            {step === 'done' && result && (
              <div className="text-center py-2 animate-[fadeInUp_0.4s_ease-out]">
                {/* Success icon */}
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-brand-purple/10 ring-4 ring-brand-purple/5">
                  <CheckCircle className="h-8 w-8 text-brand-purple" />
                </div>

                {/* Title + message */}
                <h2 className="mt-5 text-xl font-bold text-gray-900">Submission Successful</h2>
                <p className="mt-2 text-sm text-gray-500 leading-relaxed">
                  Your assignment has been successfully submitted.<br />
                  Your instructor will review your submission.
                </p>

                {/* Submission details */}
                <div className="mt-6 rounded-xl border border-gray-200 bg-gray-50/50 overflow-hidden text-left">
                  <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100">
                    <span className="text-xs text-gray-400 uppercase tracking-wide">Submission ID</span>
                    <span className="text-sm font-mono font-semibold text-gray-700 break-all text-right max-w-[60%]">{result.submissionId}</span>
                  </div>
                  <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100">
                    <span className="text-xs text-gray-400 uppercase tracking-wide">Assignment Key</span>
                    <span className="text-sm font-mono font-semibold text-gray-700">{key.trim()}</span>
                  </div>
                  <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100">
                    <span className="text-xs text-gray-400 uppercase tracking-wide">Files Detected</span>
                    <span className="text-sm font-semibold text-gray-700">{result.fileCount}</span>
                  </div>
                  <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100">
                    <span className="text-xs text-gray-400 uppercase tracking-wide">Submitted At</span>
                    <span className="text-sm font-semibold text-gray-700">{new Date().toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center px-4 py-3">
                    <span className="text-xs text-gray-400 uppercase tracking-wide">Status</span>
                    <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-green-600">
                      <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                      {result.status}
                    </span>
                  </div>
                </div>

                <p className="mt-3 text-xs text-gray-400">
                  Save your Submission ID — your instructor may need it.
                </p>

                {/* Actions */}
                <div className="mt-6 flex flex-col gap-3">
                  <Button fullWidth onClick={startOver} size="lg">
                    <RotateCcw className="h-4 w-4" /> Submit Another Assignment
                  </Button>
                  <Link to="/">
                    <Button fullWidth variant="secondary" size="lg">
                      <Home className="h-4 w-4" /> Return to Home
                    </Button>
                  </Link>
                </div>

                {/* Reassurance */}
                <p className="mt-5 text-xs text-gray-400">
                  You can close this page safely.
                </p>
              </div>
            )}
          </div>

          {/* Helper note */}
          <p className="mt-5 text-center text-sm text-gray-400">
            No login required — your submission is matched to the assignment key provided by your instructor.
          </p>
        </div>
      </div>
    </div>
  )
}
