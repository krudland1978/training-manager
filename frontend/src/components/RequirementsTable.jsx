import { useState, useEffect } from 'react'

const ROLE_OPTIONS = [
  'solution_architect',
  'cloud_engineer',
  'data_engineer',
  'devops_engineer',
  'security_engineer',
]

const GRADE_BANDS = [
  { grade_min: 1, grade_max: 3, label: 'Grades 1–3 (Junior)' },
  { grade_min: 4, grade_max: 6, label: 'Grades 4–6 (Mid)' },
  { grade_min: 7, grade_max: 8, label: 'Grades 7–8 (Senior)' },
  { grade_min: 9, grade_max: 12, label: 'Grades 9–12 (Principal+)' },
]

function buildRowKey(role_id, grade_min, grade_max) {
  return `${role_id}#${grade_min}#${grade_max}`
}

function buildInitialRows(existingRules) {
  const map = {}
  for (const rule of existingRules) {
    map[rule.rule_id] = rule
  }

  const rows = []
  for (const role of ROLE_OPTIONS) {
    for (const band of GRADE_BANDS) {
      const key = buildRowKey(role, band.grade_min, band.grade_max)
      const existing = map[key]
      rows.push({
        role_id: role,
        grade_min: band.grade_min,
        grade_max: band.grade_max,
        required_cert_ids: existing ? existing.required_cert_ids : [],
        notes: existing ? existing.notes || '' : '',
      })
    }
  }
  return rows
}

export default function RequirementsTable({ existingRules = [], certifications = [], onChange }) {
  const [rows, setRows] = useState(() => buildInitialRows(existingRules))

  useEffect(() => {
    setRows(buildInitialRows(existingRules))
  }, [existingRules])

  function toggleCert(rowIdx, certId) {
    const updated = rows.map((row, i) => {
      if (i !== rowIdx) return row
      const has = row.required_cert_ids.includes(certId)
      return {
        ...row,
        required_cert_ids: has
          ? row.required_cert_ids.filter(id => id !== certId)
          : [...row.required_cert_ids, certId],
      }
    })
    setRows(updated)
    onChange?.(updated)
  }

  function setNotes(rowIdx, value) {
    const updated = rows.map((row, i) => (i === rowIdx ? { ...row, notes: value } : row))
    setRows(updated)
    onChange?.(updated)
  }

  const activeCerts = certifications.filter(c => !c.retired)

  const thStyle = { textAlign: 'left', borderBottom: '1px solid #ddd', padding: '0.5rem', background: '#f5f5f5' }
  const tdStyle = { padding: '0.5rem', verticalAlign: 'top', borderBottom: '1px solid #eee' }

  let lastRole = null

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
      <thead>
        <tr>
          <th style={thStyle}>Role</th>
          <th style={thStyle}>Grade Band</th>
          <th style={thStyle}>Required Certifications</th>
          <th style={thStyle}>Notes</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => {
          const isNewRole = row.role_id !== lastRole
          lastRole = row.role_id
          const bandLabel = GRADE_BANDS.find(
            b => b.grade_min === row.grade_min && b.grade_max === row.grade_max
          )?.label ?? `${row.grade_min}–${row.grade_max}`

          return (
            <tr key={`${row.role_id}#${row.grade_min}#${row.grade_max}`}>
              <td style={{ ...tdStyle, fontWeight: isNewRole ? 600 : 'normal', color: isNewRole ? '#333' : '#999' }}>
                {isNewRole ? row.role_id.replace(/_/g, ' ') : ''}
              </td>
              <td style={tdStyle}>{bandLabel}</td>
              <td style={tdStyle}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                  {activeCerts.map(cert => (
                    <label key={cert.cert_id} style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={row.required_cert_ids.includes(cert.cert_id)}
                        onChange={() => toggleCert(i, cert.cert_id)}
                      />
                      <span title={cert.name}>{cert.cert_id}</span>
                    </label>
                  ))}
                </div>
              </td>
              <td style={tdStyle}>
                <input
                  type="text"
                  value={row.notes}
                  onChange={e => setNotes(i, e.target.value)}
                  placeholder="optional"
                  style={{ width: '100%', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: 4, padding: '0.25rem' }}
                />
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
