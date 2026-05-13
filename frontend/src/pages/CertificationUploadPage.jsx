import { useState } from 'react'
import FileUpload from '../components/FileUpload.jsx'
import ImportSummary from '../components/ImportSummary.jsx'
import { importCertifications, listCertifications } from '../services/api.js'

export default function CertificationUploadPage() {
  const [result, setResult] = useState(null)
  const [certs, setCerts] = useState([])
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState(null)

  async function handleUpload(file) {
    setLoading(true)
    setApiError(null)
    try {
      const summary = await importCertifications(file)
      setResult(summary)
      const { certifications } = await listCertifications()
      setCerts(certifications)
    } catch (e) {
      setApiError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '2rem auto', padding: '0 1rem' }}>
      <h1>Upload Certification Catalogue</h1>
      <p>Upload a CSV file containing available certifications.</p>
      <FileUpload onUpload={handleUpload} label="Choose certification catalogue CSV" />
      {loading && <p>Importing…</p>}
      {apiError && <p style={{ color: 'red' }}>{apiError}</p>}
      <ImportSummary result={result} />
      {certs.length > 0 && (
        <>
          <h2>Active Certifications ({certs.length})</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>{['Name', 'Level', 'Domain', 'Study Days'].map(h => (
                <th key={h} style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '0.5rem' }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {certs.map(c => (
                <tr key={c.cert_id}>
                  <td style={{ padding: '0.5rem' }}>{c.name}</td>
                  <td style={{ padding: '0.5rem' }}>{c.level}</td>
                  <td style={{ padding: '0.5rem' }}>{c.domain}</td>
                  <td style={{ padding: '0.5rem' }}>{c.effective_study_days ?? (c.typical_study_days * c.difficulty_multiplier)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  )
}
