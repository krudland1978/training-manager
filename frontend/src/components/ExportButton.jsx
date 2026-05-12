import { useState } from 'react'
import { exportPlans } from '../services/api.js'

export default function ExportButton() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleExport() {
    setLoading(true)
    setError(null)
    try {
      const blob = await exportPlans()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `training-plans-${new Date().toISOString().slice(0, 10)}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button
        onClick={handleExport}
        disabled={loading}
        style={{
          padding: '0.5rem 1.2rem',
          background: loading ? '#aaa' : '#28a745',
          color: '#fff',
          border: 'none',
          borderRadius: 6,
          cursor: loading ? 'not-allowed' : 'pointer',
          fontSize: '0.9rem',
        }}
      >
        {loading ? 'Exporting…' : 'Export CSV'}
      </button>
      {error && <span style={{ color: 'red', marginLeft: '0.5rem', fontSize: '0.85rem' }}>{error}</span>}
    </>
  )
}
