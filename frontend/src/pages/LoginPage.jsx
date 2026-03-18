
import { useState } from 'react'
import { login, signup } from '../services/api'

export default function LoginPage() {

  // "tab" controls which form is showing — 'signin' or 'signup'
  const [tab, setTab] = useState('signin')

  // --- Sign In form values ---
  const [siEmail, setSiEmail]       = useState('')
  const [siPassword, setSiPassword] = useState('')
  const [siLoading, setSiLoading]   = useState(false)
  const [siError, setSiError]       = useState('')

  // --- Sign Up form values ---
  const [suName, setSuName]         = useState('')
  const [suEmail, setSuEmail]       = useState('')
  const [suPassword, setSuPassword] = useState('')
  const [suConfirm, setSuConfirm]   = useState('')
  const [suLoading, setSuLoading]   = useState(false)
  const [suError, setSuError]       = useState('')

  // This runs when the teacher clicks "Sign In"
  async function handleSignIn(e) {
    e.preventDefault()
    setSiError('')

    if (!siEmail || !siPassword) {
      setSiError('Please fill in both fields.')
      return
    }

    setSiLoading(true)
    try {
      const data = await login(siEmail, siPassword)
      localStorage.setItem('token', data.accessToken)
      window.location.href = '/dashboard'
    } catch (err) {
      if (err.status === 401) {
        setSiError('Wrong email or password. Please try again.')
      } else {
        setSiError('Something went wrong. Please try again.')
      }
    } finally {
      setSiLoading(false)
    }
  }

  // This runs when the teacher clicks "Sign Up"
  async function handleSignUp(e) {
    e.preventDefault()
    setSuError('')

    if (!suName || !suEmail || !suPassword || !suConfirm) {
      setSuError('Please fill in all fields.')
      return
    }

    if (suPassword !== suConfirm) {
      setSuError('Passwords do not match.')
      return
    }

    setSuLoading(true)
    try {
      const data = await signup(suName, suEmail, suPassword)
      localStorage.setItem('token', data.accessToken)
      window.location.href = '/dashboard'
    } catch (err) {
      if (err.status === 409) {
        setSuError('An account with this email already exists.')
      } else {
        setSuError('Something went wrong. Please try again.')
      }
    } finally {
      setSuLoading(false)
    }
  }

  return (
    <div style={styles.page}>

      <div style={styles.navbar}>
        <span style={styles.navTitle}>Token Trail</span>
      </div>

      <div style={styles.center}>
        <div style={styles.card}>

          <h2 style={styles.title}>Teacher Portal</h2>
          <p style={styles.subtitle}>Sign in or create an account to manage assignments</p>

          <div style={styles.tabs}>
            <button
              style={tab === 'signin' ? styles.tabActive : styles.tab}
              onClick={() => { setTab('signin'); setSiError(''); setSuError('') }}
            >
              Sign In
            </button>
            <button
              style={tab === 'signup' ? styles.tabActive : styles.tab}
              onClick={() => { setTab('signup'); setSiError(''); setSuError('') }}
            >
              Sign Up
            </button>
          </div>

          {tab === 'signin' && (
            <form onSubmit={handleSignIn}>
              {siError && <p style={styles.error}>{siError}</p>}
              <div style={styles.field}>
                <label style={styles.label}>Email</label>
                <input
                  type="email"
                  value={siEmail}
                  onChange={e => setSiEmail(e.target.value)}
                  placeholder="JohnDoe@gmail.com"
                  style={styles.input}
                  disabled={siLoading}
                />
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Password</label>
                <input
                  type="password"
                  value={siPassword}
                  onChange={e => setSiPassword(e.target.value)}
                  placeholder="••••••••••"
                  style={styles.input}
                  disabled={siLoading}
                />
              </div>
              <button type="submit" style={styles.button} disabled={siLoading}>
                {siLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>
          )}

          {tab === 'signup' && (
            <form onSubmit={handleSignUp}>
              {suError && <p style={styles.error}>{suError}</p>}
              <div style={styles.field}>
                <label style={styles.label}>Email</label>
                <input
                  type="email"
                  value={suEmail}
                  onChange={e => setSuEmail(e.target.value)}
                  placeholder="JohnDoe@gmail.com"
                  style={styles.input}
                  disabled={suLoading}
                />
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Full Name</label>
                <input
                  type="text"
                  value={suName}
                  onChange={e => setSuName(e.target.value)}
                  placeholder="John Doe"
                  style={styles.input}
                  disabled={suLoading}
                />
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Password</label>
                <input
                  type="password"
                  value={suPassword}
                  onChange={e => setSuPassword(e.target.value)}
                  placeholder="••••••••••"
                  style={styles.input}
                  disabled={suLoading}
                />
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Confirm Password</label>
                <input
                  type="password"
                  value={suConfirm}
                  onChange={e => setSuConfirm(e.target.value)}
                  placeholder="••••••••••"
                  style={styles.input}
                  disabled={suLoading}
                />
              </div>
              <button type="submit" style={styles.button} disabled={suLoading}>
                {suLoading ? 'Creating account...' : 'Sign Up'}
              </button>
            </form>
          )}

        </div>
      </div>
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
  card: {
    backgroundColor: '#b0b0b0',
    borderRadius: '12px',
    padding: '32px 28px',
    width: '100%',
    maxWidth: '460px',
  },
  title: {
    textAlign: 'center',
    fontSize: '20px',
    margin: '0 0 6px 0',
  },
  subtitle: {
    textAlign: 'center',
    fontSize: '13px',
    color: '#444',
    margin: '0 0 20px 0',
  },
  tabs: {
    display: 'flex',
    backgroundColor: '#888',
    borderRadius: '8px',
    padding: '3px',
    marginBottom: '20px',
    gap: '3px',
  },
  tab: {
    flex: 1,
    padding: '10px',
    border: 'none',
    borderRadius: '6px',
    backgroundColor: 'transparent',
    color: '#ddd',
    fontSize: '14px',
    cursor: 'pointer',
    fontFamily: 'sans-serif',
  },
  tabActive: {
    flex: 1,
    padding: '10px',
    border: 'none',
    borderRadius: '6px',
    backgroundColor: '#1a1a1a',
    color: 'white',
    fontSize: '14px',
    cursor: 'pointer',
    fontFamily: 'sans-serif',
  },
  error: {
    backgroundColor: 'rgba(200,0,0,0.1)',
    border: '1px solid rgba(200,0,0,0.3)',
    borderRadius: '6px',
    color: '#a00',
    fontSize: '13px',
    padding: '10px',
    marginBottom: '12px',
    textAlign: 'center',
  },
  field: {
    marginBottom: '14px',
  },
  label: {
    display: 'block',
    fontSize: '13px',
    fontWeight: '500',
    marginBottom: '5px',
    color: '#222',
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    borderRadius: '8px',
    border: 'none',
    backgroundColor: '#e8e8e8',
    fontSize: '14px',
    fontFamily: 'sans-serif',
    boxSizing: 'border-box',
  },
  button: {
    width: '100%',
    padding: '14px',
    marginTop: '8px',
    backgroundColor: '#1a1a1a',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '15px',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontFamily: 'sans-serif',
  },
}