import { useState } from 'react'
import { login } from '../services/auth.js'

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await login(email, password)
      onLogin()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#f0f2f5',
    }}>
      <div style={{
        background: '#fff',
        padding: '2.5rem',
        borderRadius: 10,
        boxShadow: '0 2px 16px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: 380,
      }}>
        <h1 style={{ marginTop: 0, marginBottom: '0.25rem', fontSize: '1.4rem' }}>Training Manager</h1>
        <p style={{ color: '#666', marginTop: 0, marginBottom: '1.5rem', fontSize: '0.9rem' }}>Sign in to continue</p>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.3rem', fontSize: '0.9rem', fontWeight: 500 }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoFocus
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '0.6rem 0.75rem',
                border: '1px solid #ccc',
                borderRadius: 6,
                fontSize: '1rem',
              }}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.3rem', fontSize: '0.9rem', fontWeight: 500 }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '0.6rem 0.75rem',
                border: '1px solid #ccc',
                borderRadius: 6,
                fontSize: '1rem',
              }}
            />
          </div>

          {error && (
            <p style={{ color: '#cc0000', marginBottom: '1rem', fontSize: '0.9rem' }}>{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.7rem',
              background: loading ? '#aaa' : '#0066cc',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              fontSize: '1rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 600,
            }}
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
