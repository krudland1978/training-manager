const ROLES = [
  '', 'solution_architect', 'cloud_engineer', 'data_engineer',
  'devops_engineer', 'security_engineer',
]

export default function PlanFilter({ filters, onChange }) {
  function update(key, value) {
    onChange?.({ ...filters, [key]: value })
  }

  const selectStyle = {
    padding: '0.4rem 0.6rem',
    border: '1px solid #ccc',
    borderRadius: 4,
    fontSize: '0.9rem',
    marginRight: '0.75rem',
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
      <label style={{ fontSize: '0.9rem' }}>
        Role:
        <select
          value={filters.role_id || ''}
          onChange={e => update('role_id', e.target.value || undefined)}
          style={{ ...selectStyle, marginLeft: '0.4rem' }}
        >
          {ROLES.map(r => (
            <option key={r} value={r}>{r ? r.replace(/_/g, ' ') : 'All roles'}</option>
          ))}
        </select>
      </label>

      <label style={{ fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
        <input
          type="checkbox"
          checked={filters.days_warning === 'true'}
          onChange={e => update('days_warning', e.target.checked ? 'true' : undefined)}
        />
        Days warning only
      </label>
    </div>
  )
}
