// StudentSubmitPage.jsx
// This is the student submission page.
//   Step 1 — Student enters their ID and assignment key.
//   Step 2 — Student uploads their ZIP file.
//   Step 3 — Success screen showing confirmation.
import { useState, useRef } from 'react'
import { validateAssignmentKey, submitAssignment } from '../services/api'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import ErrorBanner from '../components/ui/ErrorBanner'

export default function StudentSubmitPage() {

  // "step" tracks which screen to show: 'key', 'upload', or 'done'
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

  const [result, setResult] = useState(null)

  const fileRef = useRef(null)

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
        setUploadError(err.message || 'Something is wrong with your ZIP file.')
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
    setName(''); setZipFile(null); setUploadError(''); setResult(null)
  }

  return (
    <div className="min-h-screen bg-gray-100 font-sans flex flex-col">

      {/* Navbar */}
      <div className="bg-[#3b3660] px-6 py-4 flex-shrink-0">
        <span className="text-white text-xl font-bold">Token Trail</span>
      </div>

      {/* STEP 1: enter Student ID and Key */}
      {step === 'key' && (
        <div className="flex-1 flex items-center justify-center px-4 py-12">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 w-full max-w-md p-8">
            <h1 className="text-xl font-bold text-gray-900 text-center mb-1">Submit Assignment</h1>
            <p className="text-sm text-gray-500 text-center mb-6">
              Enter your student ID and assignment key to get started.
            </p>

            <form onSubmit={handleContinue} className="flex flex-col gap-4">
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
                {keyLoading ? 'Checking…' : 'Continue'}
              </Button>
            </form>
          </div>
        </div>
      )}

      {/* STEP 2: upload ZIP */}
      {step === 'upload' && assignment && (
        <div className="flex-1 flex items-start justify-center px-4 py-12">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 w-full max-w-2xl p-8">
            <h2 className="text-xl font-bold text-gray-900 mb-1">Upload Your Assignment</h2>
            <p className="text-sm text-gray-500 mb-6">Key: <span className="font-mono">{key.trim()}</span></p>

            <form onSubmit={handleUpload} className="flex flex-col gap-5">
              <ErrorBanner message={uploadError} />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Your Name"
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="e.g. Jane Doe"
                  disabled={uploadLoading}
                />
                <Input
                  label="Student ID"
                  type="text"
                  value={studentId}
                  readOnly
                />
              </div>

              {/* Drop zone */}
              <div
                className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center cursor-pointer hover:border-[#3b3660] transition-colors"
                onClick={() => fileRef.current.click()}
              >
                <input
                  ref={fileRef}
                  type="file"
                  accept=".zip"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <p className="text-3xl mb-2">📤</p>
                <p className="text-sm font-semibold text-gray-700 mb-1">
                  {zipFile ? zipFile.name : 'Upload your Assignment'}
                </p>
                <p className="text-xs text-gray-400 mb-4">
                  {zipFile
                    ? `${(zipFile.size / 1024).toFixed(1)} KB selected`
                    : 'Select a .zip file containing your assignment'
                  }
                </p>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={e => { e.stopPropagation(); fileRef.current.click() }}
                >
                  {zipFile ? 'Change File' : 'Choose File'}
                </Button>
              </div>

              <Button type="submit" fullWidth disabled={uploadLoading} size="lg">
                {uploadLoading ? 'Uploading…' : 'Submit Assignment'}
              </Button>
            </form>
          </div>
        </div>
      )}

      {/* STEP 3: Success */}
      {step === 'done' && result && (
        <div className="flex-1 flex items-center justify-center px-4 py-12">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 w-full max-w-md p-8 text-center">
            <p className="text-5xl mb-3">✅</p>
            <h2 className="text-xl font-bold text-gray-900 mb-1">Submission Received!</h2>
            <p className="text-sm text-gray-500 mb-6">
              Save your submission ID below — your instructor may need it.
            </p>

            <div className="rounded-xl border border-gray-100 overflow-hidden mb-6 text-left">
              <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100">
                <span className="text-xs text-gray-400 uppercase tracking-wide">Submission ID</span>
                <span className="text-sm font-mono font-semibold text-gray-700 break-all text-right max-w-[60%]">{result.submissionId}</span>
              </div>
              <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100">
                <span className="text-xs text-gray-400 uppercase tracking-wide">Files Detected</span>
                <span className="text-sm font-semibold text-gray-700">{result.fileCount}</span>
              </div>
              <div className="flex justify-between items-center px-4 py-3">
                <span className="text-xs text-gray-400 uppercase tracking-wide">Status</span>
                <span className="text-sm font-semibold text-green-600">{result.status}</span>
              </div>
            </div>

            <Button fullWidth onClick={startOver}>Submit Another</Button>
          </div>
        </div>
      )}

    </div>
  )
}
