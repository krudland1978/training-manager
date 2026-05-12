import { useState } from 'react'
import { generatePlans } from '../services/api.js'

export default function PlanGenerationPage() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState(null)

  async function handleGenerate() {
    setLoading(true)
    setApiError(null)
    setResult(null)
    try {
      const summary = await generatePlans()
      setResult(summary)
    } catch (e) {
      setApiError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 700, margin: '2rem auto', padding: '0 1rem' }}>
      <h1>Generate Training Plans</h1>
      <p>
        Click below to generate an individualised training plan for each active team member
        based on their role, grade, certifications held, and the requirements matrix.
        Any existing plans will be replaced.
      </p>

      <button
        onClick={handleGenerate}
        disabled={loading}
        style={{
          padding: '0.7rem 1.8rem',
          background: loading ? '#aaa' : '#0066cc',
          color: '#fff',
          border: 'none',
          borderRadius: 6,
          cursor: loading ? 'not-allowed' : 'pointer',
          fontSize: '1rem',
        }}
      >
        {loading ? 'Generating…' : 'Generate Plans'}
      </button>

      {apiError && (
        <p style={{ color: 'red', marginTop: '1rem' }}>{apiError}</p>
      )}

      {result && (
        <div style={{ marginTop: '1.5rem', padding: '1rem', background: '#f0f9f0', border: '1px solid #c3e6cb', borderRadius: 6 }}>
          <h3 style={{ marginBottom: '0.5rem', color: '#155724' }}>Generation Complete</h3>
          <ul style={{ margin: 0, paddingLeft: '1.2rem', lineHeight: 1.8 }}>
            <li><strong>{result.generated}</strong> plans generated</li>
            <li><strong>{result.requirement_met}</strong> already met all requirements</li>
            <li><strong>{result.no_requirement}</strong> with no matching rule</li>
            <li><strong>{result.days_warnings}</strong> approaching their training day limit</li>
          </ul>
          {result.errors?.length > 0 && (
            <details style={{ marginTop: '0.75rem' }}>
              <summary style={{ cursor: 'pointer', color: '#856404' }}>
                {result.errors.length} member{result.errors.length !== 1 ? 's' : ''} skipped
              </summary>
              <ul style={{ marginTop: '0.5rem' }}>
                {result.errors.map((e, i) => (
                  <li key={i}><code>{e.person_id}</code>: {e.reason}</li>
                ))}
              </ul>
            </details>
          )}
          <p style={{ marginTop: '0.75rem', marginBottom: 0 }}>
            <a href="/plans" style={{ color: '#0066cc' }}>View plans dashboard →</a>
          </p>
        </div>
      )}
    </div>
  )
}
