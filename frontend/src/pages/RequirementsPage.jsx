import { useState, useEffect } from 'react'
import RequirementsTable from '../components/RequirementsTable.jsx'
import { getRequirements, saveRequirements, listCertifications } from '../services/api.js'

export default function RequirementsPage() {
  const [existingRules, setExistingRules] = useState([])
  const [certifications, setCertifications] = useState([])
  const [pendingRows, setPendingRows] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [apiError, setApiError] = useState(null)
  const [saveResult, setSaveResult] = useState(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      setApiError(null)
      try {
        const [reqData, certData] = await Promise.all([
          getRequirements(),
          listCertifications(),
        ])
        setExistingRules(reqData.rules || [])
        setCertifications(certData.certifications || [])
      } catch (e) {
        setApiError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  async function handleSave() {
    const rows = pendingRows ?? buildDefaultRules(existingRules)
    const rules = rows
      .filter(r => r.required_cert_ids.length > 0)
      .map(r => ({
        role_id: r.role_id,
        grade_min: r.grade_min,
        grade_max: r.grade_max,
        required_cert_ids: r.required_cert_ids,
        notes: r.notes || undefined,
      }))

    setSaving(true)
    setApiError(null)
    setSaveResult(null)
    try {
      const result = await saveRequirements(rules)
      setSaveResult(result)
      const refreshed = await getRequirements()
      setExistingRules(refreshed.rules || [])
      setPendingRows(null)
    } catch (e) {
      setApiError(e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ maxWidth: 1100, margin: '2rem auto', padding: '0 1rem' }}>
      <h1>Certification Requirements Matrix</h1>
      <p>Define which certifications are required for each role and grade band. Tick the certifications required; unticked rows are excluded from the matrix.</p>

      {loading && <p>Loading…</p>}
      {apiError && <p style={{ color: 'red' }}>{apiError}</p>}

      {saveResult && (
        <p style={{ color: 'green' }}>
          Saved {saveResult.saved} rule{saveResult.saved !== 1 ? 's' : ''}.
          {saveResult.warnings?.length > 0 && ` ${saveResult.warnings.length} warning(s).`}
        </p>
      )}

      {!loading && (
        <>
          <RequirementsTable
            existingRules={existingRules}
            certifications={certifications}
            onChange={setPendingRows}
          />
          <div style={{ marginTop: '1.5rem' }}>
            <button
              onClick={handleSave}
              disabled={saving}
              style={{
                padding: '0.6rem 1.5rem',
                background: '#0066cc',
                color: '#fff',
                border: 'none',
                borderRadius: 6,
                cursor: saving ? 'not-allowed' : 'pointer',
                fontSize: '1rem',
              }}
            >
              {saving ? 'Saving…' : 'Save Requirements'}
            </button>
          </div>
        </>
      )}
    </div>
  )
}

function buildDefaultRules(existing) {
  return existing.map(r => ({
    role_id: r.role_id,
    grade_min: r.grade_min,
    grade_max: r.grade_max,
    required_cert_ids: r.required_cert_ids,
    notes: r.notes || '',
  }))
}
