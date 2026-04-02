import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login, signup } from '../services/api'
import { FileText, Loader2, ClipboardList, BarChart3, Columns } from 'lucide-react'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import ErrorBanner from '../components/ui/ErrorBanner'

const VALUE_POINTS = [
  { icon: ClipboardList, text: 'Manage assignments and collect submissions' },
  { icon: BarChart3, text: 'Review similarity results and confidence scores' },
  { icon: Columns, text: 'Compare flagged submissions side by side' },
]

export default function LoginPage() {
  const [tab, setTab] = useState('signin')
  const navigate = useNavigate()

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
      navigate('/dashboard')
    } catch (err) {
      setSiError(
        err.status === 401
          ? 'Wrong email or password. Please try again.'
          : 'Something went wrong. Please try again.'
      )
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
      navigate('/dashboard')
    } catch (err) {
      setSuError(
        err.status === 409
          ? 'An account with this email already exists.'
          : 'Something went wrong. Please try again.'
      )
    } finally {
      setSuLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-screen flex-col bg-[radial-gradient(circle_at_top,rgba(86,79,103,0.06),transparent_60%),_#FEF7FF66]">
      {/* Header band — compact, matching landing page nav bar */}
      <header className="relative bg-landing px-6 pb-7 pt-5">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-2.5 lg:items-start">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/15">
              <FileText className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-semibold text-white tracking-tight">Token Trail</span>
          </Link>
        </div>
      </header>

      {/* Radial glow — soft emphasis behind the auth area */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[500px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(ellipse_at_center,rgba(120,109,145,0.08),transparent_70%)]" />

      {/* Content */}
      <div className="relative z-10 flex flex-1 items-start justify-center px-4 pt-6 pb-12">
        <div className="flex w-full justify-center relative">
          <div className="w-80 mr-4"/>
          {/* Auth card column */}
          <div className="w-full max-w-lg mx-auto lg:mx-0">
            {/* Card */}
            <div className="rounded-2xl border border-white/60 bg-white px-10 py-9 ring-1 ring-black/5 shadow-xl hover:shadow-2xl transition-shadow duration-300">
              <h1 className="text-xl font-bold text-gray-900 text-center mb-1">Instructor Portal</h1>
              <p className="text-sm text-gray-500 text-center mb-6">
                Sign in or create an account to get started
              </p>

              {/* Tab switcher — segmented control */}
              <div className="flex gap-1 rounded-xl bg-gray-100 p-1 mb-6">
                <button
                  className={`flex-1 rounded-lg py-2.5 text-sm font-semibold transition-all ${
                    tab === 'signin'
                      ? 'bg-brand-purple text-white shadow-sm'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                  onClick={() => { setTab('signin'); setSiError(''); setSuError('') }}
                >
                  Sign In
                </button>
                <button
                  className={`flex-1 rounded-lg py-2.5 text-sm font-semibold transition-all ${
                    tab === 'signup'
                      ? 'bg-brand-purple text-white shadow-sm'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                  onClick={() => { setTab('signup'); setSiError(''); setSuError('') }}
                >
                  Sign Up
                </button>
              </div>

              {/* Sign In form */}
              {tab === 'signin' && (
                <form onSubmit={handleSignIn} className="flex flex-col gap-4">
                  <ErrorBanner message={siError} />
                  <Input
                    label="Email"
                    type="email"
                    value={siEmail}
                    onChange={e => setSiEmail(e.target.value)}
                    placeholder="you@university.edu"
                    disabled={siLoading}
                  />
                  <Input
                    label="Password"
                    type="password"
                    value={siPassword}
                    onChange={e => setSiPassword(e.target.value)}
                    placeholder="••••••••"
                    disabled={siLoading}
                  />
                  <Button type="submit" fullWidth disabled={siLoading} size="lg" className="mt-2">
                    {siLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                    {siLoading ? 'Signing in…' : 'Sign In'}
                  </Button>
                </form>
              )}

              {/* Sign Up form */}
              {tab === 'signup' && (
                <form onSubmit={handleSignUp} className="flex flex-col gap-4">
                  <ErrorBanner message={suError} />
                  <Input
                    label="Full Name"
                    type="text"
                    value={suName}
                    onChange={e => setSuName(e.target.value)}
                    placeholder="Jane Doe"
                    disabled={suLoading}
                  />
                  <Input
                    label="Email"
                    type="email"
                    value={suEmail}
                    onChange={e => setSuEmail(e.target.value)}
                    placeholder="you@university.edu"
                    disabled={suLoading}
                  />
                  <Input
                    label="Password"
                    type="password"
                    value={suPassword}
                    onChange={e => setSuPassword(e.target.value)}
                    placeholder="••••••••"
                    disabled={suLoading}
                  />
                  <Input
                    label="Confirm Password"
                    type="password"
                    value={suConfirm}
                    onChange={e => setSuConfirm(e.target.value)}
                    placeholder="••••••••"
                    disabled={suLoading}
                  />
                  <Button type="submit" fullWidth disabled={suLoading} size="lg" className="mt-2">
                    {suLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                    {suLoading ? 'Creating account…' : 'Sign Up'}
                  </Button>
                </form>
              )}
            </div>

            <p className="mt-5 text-center text-xs text-gray-400 lg:text-left">
              &copy; {new Date().getFullYear()} Token Trail. Built for academic integrity.
            </p>
          </div>
          <div className="w-80 h-fit rounded-xl ml-4 border border-gray-200 bg-gray-50 px-5 py-4">
            <p className="text-xs leading-relaxed text-gray-500">
              Token Trail uses token-based and winnowing analysis to detect structural
              similarity in student code submissions. Results are advisory and intended
              to support — not replace — academic judgment.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
