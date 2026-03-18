import { useState } from 'react'
import { login, signup } from '../services/api'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import ErrorBanner from '../components/ui/ErrorBanner'

export default function LoginPage() {
  const [tab, setTab] = useState('signin')

  const [siEmail, setSiEmail]       = useState('')
  const [siPassword, setSiPassword] = useState('')
  const [siLoading, setSiLoading]   = useState(false)
  const [siError, setSiError]       = useState('')

  const [suName, setSuName]         = useState('')
  const [suEmail, setSuEmail]       = useState('')
  const [suPassword, setSuPassword] = useState('')
  const [suConfirm, setSuConfirm]   = useState('')
  const [suLoading, setSuLoading]   = useState(false)
  const [suError, setSuError]       = useState('')

  async function handleSignIn(e) {
    e.preventDefault()
    setSiError('')
    if (!siEmail || !siPassword) { setSiError('Please fill in both fields.'); return }
    setSiLoading(true)
    try {
      const data = await login(siEmail, siPassword)
      localStorage.setItem('token', data.accessToken)
      window.location.href = '/dashboard'
    } catch (err) {
      setSiError(err.status === 401 ? 'Wrong email or password. Please try again.' : 'Something went wrong. Please try again.')
    } finally {
      setSiLoading(false)
    }
  }

  async function handleSignUp(e) {
    e.preventDefault()
    setSuError('')
    if (!suName || !suEmail || !suPassword || !suConfirm) { setSuError('Please fill in all fields.'); return }
    if (suPassword !== suConfirm) { setSuError('Passwords do not match.'); return }
    setSuLoading(true)
    try {
      const data = await signup(suName, suEmail, suPassword)
      localStorage.setItem('token', data.accessToken)
      window.location.href = '/dashboard'
    } catch (err) {
      setSuError(err.status === 409 ? 'An account with this email already exists.' : 'Something went wrong. Please try again.')
    } finally {
      setSuLoading(false)
    }
  }

  const tabBase = 'flex-1 py-2 text-sm font-semibold rounded-lg transition-colors'
  const tabActive = 'bg-[#3b3660] text-white shadow-sm'
  const tabInactive = 'text-gray-500 hover:text-gray-700'

  return (
    <div className="min-h-screen bg-gray-100 font-sans flex flex-col">
      {/* Navbar */}
      <div className="bg-[#3b3660] px-6 py-4 flex-shrink-0">
        <span className="text-white text-xl font-bold">Token Trail</span>
      </div>

      {/* Centered card */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 w-full max-w-md p-8">

          <h1 className="text-xl font-bold text-gray-900 text-center mb-1">Teacher Portal</h1>
          <p className="text-sm text-gray-500 text-center mb-6">Sign in or create an account to manage assignments</p>

          {/* Tab switcher */}
          <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-6">
            <button className={`${tabBase} ${tab === 'signin' ? tabActive : tabInactive}`}
              onClick={() => { setTab('signin'); setSiError(''); setSuError('') }}>
              Sign In
            </button>
            <button className={`${tabBase} ${tab === 'signup' ? tabActive : tabInactive}`}
              onClick={() => { setTab('signup'); setSiError(''); setSuError('') }}>
              Sign Up
            </button>
          </div>

          {/* Sign In form */}
          {tab === 'signin' && (
            <form onSubmit={handleSignIn} className="flex flex-col gap-4">
              <ErrorBanner message={siError} />
              <Input label="Email" type="email" value={siEmail}
                onChange={e => setSiEmail(e.target.value)}
                placeholder="you@university.edu" disabled={siLoading} />
              <Input label="Password" type="password" value={siPassword}
                onChange={e => setSiPassword(e.target.value)}
                placeholder="••••••••" disabled={siLoading} />
              <Button type="submit" fullWidth disabled={siLoading} size="lg" className="mt-1">
                {siLoading ? 'Signing in…' : 'Sign In'}
              </Button>
            </form>
          )}

          {/* Sign Up form */}
          {tab === 'signup' && (
            <form onSubmit={handleSignUp} className="flex flex-col gap-4">
              <ErrorBanner message={suError} />
              <Input label="Email" type="email" value={suEmail}
                onChange={e => setSuEmail(e.target.value)}
                placeholder="you@university.edu" disabled={suLoading} />
              <Input label="Full Name" type="text" value={suName}
                onChange={e => setSuName(e.target.value)}
                placeholder="Jane Doe" disabled={suLoading} />
              <Input label="Password" type="password" value={suPassword}
                onChange={e => setSuPassword(e.target.value)}
                placeholder="••••••••" disabled={suLoading} />
              <Input label="Confirm Password" type="password" value={suConfirm}
                onChange={e => setSuConfirm(e.target.value)}
                placeholder="••••••••" disabled={suLoading} />
              <Button type="submit" fullWidth disabled={suLoading} size="lg" className="mt-1">
                {suLoading ? 'Creating account…' : 'Sign Up'}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
