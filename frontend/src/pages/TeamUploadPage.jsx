import { useState } from 'react'
import FileUpload from '../components/FileUpload.jsx'
import ImportSummary from '../components/ImportSummary.jsx'
import { importTeamMembers, listTeamMembers } from '../services/api.js'

export default function TeamUploadPage() {
  const [result, setResult] = useState(null)
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState(null)

  async function handleUpload(file) {
    setLoading(true)
    setApiError(null)
    try {
      const summary = await importTeamMembers(file)
      setResult(summary)
      const { members: list } = await listTeamMembers({ active: 'true' })
      setMembers(list)
    } catch (e) {
      setApiError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '2rem auto', padding: '0 1rem' }}>
      <h1>Upload Team Roster</h1>
      <p>Upload a CSV file containing your team members. Required columns: person_id, name, email, grade_level, role_id, start_date, grade_start_date, manager_email, location, active, days_allocated_override, days_remaining, certifications_held.</p>
      <FileUpload onUpload={handleUpload} label="Choose team roster CSV" />
      {loading && <p>Importing…</p>}
      {apiError && <p style={{ color: 'red' }}>{apiError}</p>}
      <ImportSummary result={result} />
      {members.length > 0 && (
        <>
          <h2>Active Team Members ({members.length})</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>{['Name', 'Role', 'Grade', 'Location', 'Days Remaining'].map(h => (
                <th key={h} style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '0.5rem' }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {members.map(m => (
                <tr key={m.person_id}>
                  <td style={{ padding: '0.5rem' }}>{m.name}</td>
                  <td style={{ padding: '0.5rem' }}>{m.role_id}</td>
                  <td style={{ padding: '0.5rem' }}>{m.grade_level}</td>
                  <td style={{ padding: '0.5rem' }}>{m.location}</td>
                  <td style={{ padding: '0.5rem' }}>{m.days_remaining}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  )
}
