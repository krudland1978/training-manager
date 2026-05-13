import DaysWarningBadge from './DaysWarningBadge.jsx'

export default function MemberPlanDetail({ plan }) {
  if (!plan) return null

  const tdStyle = { padding: '0.4rem 0.6rem', borderBottom: '1px solid #eee' }

  return (
    <div style={{ marginTop: '1.5rem' }}>
      <h3 style={{ marginBottom: '0.5rem' }}>{plan.name}</h3>
      <p style={{ color: '#555', marginBottom: '0.75rem' }}>
        {plan.role_id?.replace(/_/g, ' ')} · Grade {plan.grade_level}
        {plan.days_remaining !== undefined && plan.days_remaining !== null && (
          <span> · {plan.days_remaining} training days remaining</span>
        )}
        {' '}
        <DaysWarningBadge daysRemaining={plan.days_remaining} daysRequired={plan.total_study_days_required} />
      </p>

      {plan.no_requirement && (
        <p style={{ color: '#666', fontStyle: 'italic' }}>No certification requirement defined for this role/grade.</p>
      )}

      {plan.requirement_met && !plan.no_requirement && (
        <p style={{ color: 'green', fontWeight: 600 }}>All required certifications are held.</p>
      )}

      {plan.required_cert_ids?.length > 0 && (
        <div style={{ marginBottom: '0.75rem' }}>
          <strong>Required:</strong>{' '}
          {plan.required_cert_ids.map(id => (
            <span
              key={id}
              style={{
                display: 'inline-block',
                background: plan.certs_held?.includes(id) ? '#d4edda' : '#f8d7da',
                color: plan.certs_held?.includes(id) ? '#155724' : '#721c24',
                borderRadius: 4,
                padding: '0.1rem 0.4rem',
                marginRight: '0.25rem',
                fontSize: '0.85rem',
              }}
            >
              {id}
            </span>
          ))}
        </div>
      )}

      {plan.outstanding_certs?.length > 0 && (
        <>
          <h4 style={{ marginBottom: '0.4rem' }}>Outstanding Certifications</h4>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
            <thead>
              <tr>
                {['Certification', 'Level', 'Study Days'].map(h => (
                  <th key={h} style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: '0.4rem 0.6rem', background: '#f5f5f5' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {plan.outstanding_certs.map(cert => (
                <tr key={cert.cert_id}>
                  <td style={tdStyle}>{cert.name}</td>
                  <td style={tdStyle}>{cert.level}</td>
                  <td style={tdStyle}>{Math.ceil(cert.effective_study_days)}</td>
                </tr>
              ))}
              <tr>
                <td style={{ ...tdStyle, fontWeight: 600 }} colSpan={2}>Total</td>
                <td style={{ ...tdStyle, fontWeight: 600 }}>{Math.ceil(plan.total_study_days_required)}</td>
              </tr>
            </tbody>
          </table>
        </>
      )}
    </div>
  )
}
