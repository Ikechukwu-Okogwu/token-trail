import { useState } from 'react'
import { apiFetch } from '../services/api'

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      localStorage.setItem('token', data.accessToken)
      onLogin()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#f0f0f4] flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-lg p-10 w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[#3b3660] tracking-tight">Token Trail</h1>
          <p className="text-sm text-gray-500 mt-1">Instructor Portal</p>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
              placeholder="alice@example.com"
              className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]/40"/>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
              placeholder="••••••••"
              className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#3b3660]/40"/>
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading}
            className="bg-[#3b3660] text-white rounded-xl py-3 text-sm font-semibold hover:bg-[#2d2b4a] disabled:opacity-60 transition-colors mt-1">
            {loading ? 'Logging in…' : 'Log In'}
          </button>
        </form>
      </div>
    </div>
  )
}
