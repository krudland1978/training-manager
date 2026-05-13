import { useState, useEffect } from 'react'
import { getPlansStatus } from '../services/api.js'

export default function StalePlansBanner() {
  const [stale, setStale] = useState(false)

  useEffect(() => {
    getPlansStatus()
      .then(data => setStale(data?.plans_stale ?? false))
      .catch(() => {})
  }, [])

  if (!stale) return null

  return (
    <div style={{
      background: '#fff3cd',
      border: '1px solid #ffc107',
      borderRadius: 6,
      padding: '0.75rem 1rem',
      marginBottom: '1rem',
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
    }}>
      <span style={{ fontSize: '1.2rem' }}>⚠</span>
      <span>
        Plans are outdated — team data or requirements have changed.{' '}
        <a href="/generate" style={{ color: '#856404', fontWeight: 600 }}>Regenerate plans →</a>
      </span>
    </div>
  )
}
