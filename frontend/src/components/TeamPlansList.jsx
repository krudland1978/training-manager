import DaysWarningBadge from './DaysWarningBadge.jsx'

export default function TeamPlansList({ plans, onSelect, selectedPersonId }) {
  if (!plans || plans.length === 0) {
    return <p style={{ color: '#666', fontStyle: 'italic' }}>No plans to display.</p>
  }

  const thStyle = { textAlign: 'left', borderBottom: '2px solid #ddd', padding: '0.5rem', background: '#f5f5f5' }
  const tdStyle = { padding: '0.5rem', borderBottom: '1px solid #eee' }

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
      <thead>
        <tr>
          {['Name', 'Role', 'Grade', 'Outstanding', 'Study Days', 'Days Left', 'Status'].map(h => (
            <th key={h} style={thStyle}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {plans.map(plan => (
          <tr
            key={plan.person_id}
            onClick={() => onSelect?.(plan.person_id)}
            style={{
              cursor: onSelect ? 'pointer' : 'default',
              background: selectedPersonId === plan.person_id ? '#e8f0fe' : undefined,
            }}
          >
            <td style={tdStyle}>{plan.name}</td>
            <td style={tdStyle}>{plan.role_id?.replace(/_/g, ' ')}</td>
            <td style={tdStyle}>{plan.grade_level}</td>
            <td style={tdStyle}>{plan.no_requirement ? '—' : plan.outstanding_count}</td>
            <td style={tdStyle}>
              {plan.no_requirement ? '—' : Math.ceil(plan.total_study_days_required)}
            </td>
            <td style={tdStyle}>{plan.days_remaining ?? '—'}</td>
            <td style={tdStyle}>
              {plan.no_requirement && <span style={{ color: '#666' }}>No rule</span>}
              {!plan.no_requirement && plan.requirement_met && <span style={{ color: 'green' }}>Complete</span>}
              {!plan.no_requirement && !plan.requirement_met && (
                plan.days_warning
                  ? <DaysWarningBadge daysRemaining={plan.days_remaining} daysRequired={plan.total_study_days_required} />
                  : <span style={{ color: '#0066cc' }}>In progress</span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
