// StudentSubmitPage.jsx
// This is the student submission page.
//   Step 1— Student enters their ID and assignment key.
//   Step 2— Student uploads their ZIP file.
//   Step 3 — Success screen showing confirmation.
import { useState, useRef } from 'react'
import { validateAssignmentKey, submitAssignment } from '../services/api'

export default function StudentSubmitPage() {

  // "step" tracks which screen to show
  // It can be:'key, upload, or done
  const [step, setStep] = useState('key')
  // --values ---
  const [studentId, setStudentId] = useState('')  //students ID number
  const [key, setKey] = useState('')  //assignment key
  const [keyLoading, setKeyLoading] = useState(false)
  const [keyError, setKeyError] = useState('')
  const [assignment, setAssignment] = useState(null) //info returned from server

  const [name, setName] = useState('')  // student's name (optional)
  const [zipFile, setZipFile] = useState(null) // the ZIP file they choose
  const [uploadLoading, setUploadLoading] = useState(false)
  const [uploadError, setUploadError] = useState('')

  // --- Step 3 values ---
  const [result, setResult] = useState(null) // confirmation from server

  // The ref lets us trigger the hidden file input
  const fileRef = useRef(null)

  // ---- first we check the assignment key ----
  async function handleContinue(e) {
    e.preventDefault()
    setKeyError('')

    // Make sure fields are not empty
    if (!studentId) { setKeyError('Please enter your Student ID.'); return }
    if (!key)       { setKeyError('Please enter your Assignment Key.'); return }

    setKeyLoading(true)
    try {
      // Asking the backend if this key is valid and Returns: { valid: true/false, assignment: { id, language, isOpen } }
      const data = await validateAssignmentKey(key.trim())

      if (!data.valid || !data.assignment) {
        setKeyError('Assignment key not found. Check with your instructor!')
        return
      }

      if (!data.assignment.isOpen) {
        setKeyError('This assignment is closed and not accepting submissions.')
        return
      }
      // If Key is valid then save the assignment info and move to step 2
      setAssignment(data.assignment)
      setStep('upload')

    } catch (err) {
      setKeyError('Could not reach the server. Please try again.')
    } finally {
      setKeyLoading(false)
    }
  }

  // ----  Upload the ZIP file ----
  function handleFileChange(e) {
    const file = e.target.files[0]
    if (!file) return

    // Make sure its a zip file
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
      // Send the ZIP file to the backend
      const data = await submitAssignment({
        assignmentKey: key.trim(),
        studentIdentifier: studentId.trim(),
        studentName: name.trim() || undefined,
        zipFile: zipFile,
      })
      // Save the result and move to success screen
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
  // Reset everything and go back to step 1
  function startOver() {
    setStep('key')
    setStudentId(''); setKey(''); setKeyError(''); setAssignment(null)
    setName(''); setZipFile(null); setUploadError(''); setResult(null)
  }

  return (
    <div style={styles.page}>

      {/* Top navbar */}
      <div style={styles.navbar}>
        <span style={styles.navTitle}>Token Trail</span>
      </div>

      {/* --STEP 1: enter Student ID and Key--*/}
      {step === 'key' && (
        <div style={styles.center}>
          <form onSubmit={handleContinue} style={styles.keyForm}>
            <p style={styles.instruction}>
              Enter your student ID and assignment key to submit your project!
            </p>
            {/* Show error if there is one */}
            {keyError && <p style={styles.error}>{keyError}</p>}

            <div style={styles.field}>
              <label style={styles.label}>Student ID</label>
              <input
                type="text"
                value={studentId}
                onChange={e => { setStudentId(e.target.value); setKeyError('') }}
                placeholder="e.g 5342145"
                style={styles.inputRound}
                disabled={keyLoading}
              />
            </div>

            <div style={styles.field}>
              <label style={styles.label}>Assignment Key</label>
              <input
                type="text"
                value={key}
                onChange={e => { setKey(e.target.value); setKeyError('') }}
                placeholder="e.g ASSIGN-0234-ABC"
                style={styles.inputRound}
                disabled={keyLoading}
              />
            </div>

            <button type="submit" style={styles.buttonRound} disabled={keyLoading}>
              {keyLoading ? 'Checking...' : 'Continue'}
            </button>

          </form>
        </div>
      )}

      {/* -STEP 2: upload ZIP -*/}
      {step === 'upload' && assignment && (
        <div style={styles.uploadLayout}>

          {/* Sidebar */}
          <div style={styles.sidebar}>
            <a href="/" style={styles.sidebarLink}>Home</a>
            <div style={styles.sidebarLinkActive}>Upload Assignment</div>
          </div>

          {/* Main upload area */}
          <div style={styles.uploadMain}>
            <div style={styles.uploadCard}>

              <h3 style={styles.uploadTitle}>Assignment Submission</h3>
              <p style={styles.uploadSub}>Assignment Key: {key.trim()}</p>

              {uploadError && <p style={styles.error}>{uploadError}</p>}

              <form onSubmit={handleUpload}>

                {/* Name and a note about student ID */}
                <div style={styles.twoCol}>
                  <div style={styles.field}>
                    <label style={styles.label}>Your Name</label>
                    <input
                      type="text"
                      value={name}
                      onChange={e => setName(e.target.value)}
                      placeholder="e.g John Doe"
                      style={styles.input}
                      disabled={uploadLoading}
                    />
                  </div>
                  <div style={styles.field}>
                    <label style={styles.label}>Student ID</label>
                    {/* Show the student ID they already entered — read only */}
                    <input
                      type="text"
                      value={studentId}
                      style={styles.input}
                      readOnly
                    />
                  </div>
                </div>

                {/* zip file drop zone */}
                <div style={styles.dropZone} onClick={() => fileRef.current.click()}>

                  {/* Hidden file input */}
                  <input
                    ref={fileRef}
                    type="file"
                    accept=".zip"
                    style={{ display: 'none' }}
                    onChange={handleFileChange}
                  />

                  <p style={styles.dropIcon}>📤</p>
                  <p style={styles.dropTitle}>
                    {zipFile ? zipFile.name : 'Upload your Assignment'}
                  </p>
                  <p style={styles.dropSub}>
                    {zipFile
                      ? `${(zipFile.size / 1024).toFixed(1)} KB selected`
                      : 'Select a .zip file containing your assignment'
                    }
                  </p>

                  <button
                    type="button"
                    style={styles.chooseBtn}
                    onClick={e => { e.stopPropagation(); fileRef.current.click() }}
                  >
                    {zipFile ? 'Change File' : 'Choose File'}
                  </button>

                </div>

                <button
                  type="submit"
                  style={{ ...styles.buttonRound, marginTop: '16px' }}
                  disabled={uploadLoading}
                >
                  {uploadLoading ? 'Uploading...' : 'Submit Assignment'}
                </button>

              </form>
            </div>
          </div>

        </div>
      )}

      {/* -STEP 3: Success-*/}
      {step === 'done' && result && (
        <div style={styles.center}>
          <div style={styles.successCard}>

            <p style={styles.successIcon}></p>
            <h2>Submission Received!</h2>
            <p style={{ color: '#555' }}>
              Save your submission ID below — your instructor may need it.
            </p>

            {/*Show the details from the server*/}
            <div style={styles.resultBox}>
              <div style={styles.resultRow}>
                <span style={styles.resultLabel}>Submission ID</span>
                <span style={styles.resultValue}>{result.submissionId}</span>
              </div>
              <div style={styles.resultRow}>
                <span style={styles.resultLabel}>Files Detected</span>
                <span style={styles.resultValue}>{result.fileCount}</span>
              </div>
              <div style={styles.resultRow}>
                <span style={styles.resultLabel}>Status</span>
                <span style={{ ...styles.resultValue, color: 'green' }}>{result.status}</span>
              </div>
            </div>

            <button style={styles.buttonRound} onClick={startOver}>
              Submit Another
            </button>

          </div>
        </div>
      )}

    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    backgroundColor: '#c8c8c8',
    fontFamily: 'sans-serif',
  },
  navbar: {
    backgroundColor: '#3d3d5c',
    padding: '16px 24px',
  },
  navTitle: {
    color: 'white',
    fontSize: '20px',
    fontWeight: 'bold',
  },
  center: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '60px 24px',
  },
  keyForm: {
    width: '100%',
    maxWidth: '600px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  instruction: {
    textAlign: 'center',
    fontSize: '15px',
    color: '#222',
    margin: '0 0 8px 0',
  },
  error: {
    backgroundColor: 'rgba(200,0,0,0.1)',
    border: '1px solid rgba(200,0,0,0.3)',
    borderRadius: '6px',
    color: '#a00',
    fontSize: '13px',
    padding: '10px',
    textAlign: 'center',
    margin: '0',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  label: {
    fontSize: '13px',
    fontWeight: '500',
    color: '#222',
  },
  inputRound: {
    padding: '13px 18px',
    borderRadius: '24px',
    border: 'none',
    backgroundColor: '#e8e8e8',
    fontSize: '14px',
    fontFamily: 'sans-serif',
    width: '100%',
    boxSizing: 'border-box',
  },
  input: {
    padding: '12px 16px',
    borderRadius: '8px',
    border: 'none',
    backgroundColor: '#e8e8e8',
    fontSize: '14px',
    fontFamily: 'sans-serif',
    width: '100%',
    boxSizing: 'border-box',
  },
  buttonRound: {
    width: '100%',
    padding: '14px',
    backgroundColor: '#1a1a1a',
    color: 'white',
    border: 'none',
    borderRadius: '24px',
    fontSize: '15px',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontFamily: 'sans-serif',
  },

  //Upload layout
  uploadLayout: {
    display: 'flex',
    minHeight: 'calc(100vh - 54px)',
  },
  sidebar: {
    width: '180px',
    backgroundColor: 'white',
    padding: '16px 0',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  sidebarLink: {
    padding: '10px 20px',
    fontSize: '14px',
    color: '#555',
    textDecoration: 'none',
    display: 'block',
  },
  sidebarLinkActive: {
    padding: '10px 20px',
    fontSize: '14px',
    color: '#1a1a1a',
    fontWeight: 'bold',
    backgroundColor: '#e8e8e8',
  },
  uploadMain: {
    flex: 1,
    padding: '32px',
  },
  uploadCard: {
    backgroundColor: '#b0b0b0',
    borderRadius: '12px',
    padding: '28px',
    maxWidth: '780px',
  },
  uploadTitle: {
    fontSize: '18px',
    margin: '0 0 4px 0',
  },
  uploadSub: {
    fontSize: '13px',
    color: '#444',
    margin: '0 0 20px 0',
  },
  twoCol: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px',
    marginBottom: '20px',
  },
  dropZone: {
    border: '2px dashed #888',
    borderRadius: '8px',
    padding: '40px 20px',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: 'rgba(0,0,0,0.05)',
  },
  dropIcon: {
    fontSize: '36px',
    margin: '0 0 8px 0',
  },
  dropTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    margin: '0 0 6px 0',
    color: '#1a1a1a',
  },
  dropSub: {
    fontSize: '12px',
    color: '#555',
    margin: '0 0 12px 0',
  },
  chooseBtn: {
    backgroundColor: '#e8e8e8',
    border: 'none',
    borderRadius: '20px',
    padding: '8px 20px',
    fontSize: '13px',
    cursor: 'pointer',
    fontFamily: 'sans-serif',
  },

  //Success screen
  successCard: {
    backgroundColor: '#b0b0b0',
    borderRadius: '12px',
    padding: '40px',
    maxWidth: '480px',
    width: '100%',
    textAlign: 'center',
  },
  successIcon: {
    fontSize: '48px',
    margin: '0 0 8px 0',
  },
  resultBox: {
    backgroundColor: 'rgba(0,0,0,0.08)',
    borderRadius: '8px',
    overflow: 'hidden',
    margin: '20px 0',
    textAlign: 'left',
  },
  resultRow: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px 16px',
    borderBottom: '1px solid rgba(0,0,0,0.08)',
  },
  resultLabel: {
    fontSize: '13px',
    color: '#555',
  },
  resultValue: {
    fontSize: '13px',
    fontWeight: '600',
    color: '#1a1a1a',
    wordBreak: 'break-all',
    maxWidth: '55%',
    textAlign: 'right',
  },
}
