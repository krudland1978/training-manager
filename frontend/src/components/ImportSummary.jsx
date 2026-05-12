export default function ImportSummary({ result }) {
  if (!result) return null
  const { imported, skipped, warnings = [], errors = [] } = result

  return (
    <div style={{ marginTop: '1rem' }}>
      <p>
        <strong>{imported}</strong> imported &nbsp;|&nbsp;
        <strong>{skipped}</strong> skipped
        {warnings.length > 0 && <span> &nbsp;|&nbsp; <strong>{warnings.length}</strong> warnings</span>}
      </p>
      {warnings.length > 0 && (
        <details>
          <summary style={{ cursor: 'pointer', color: '#b36a00' }}>Warnings ({warnings.length})</summary>
          <ul>
            {warnings.map((w, i) => (
              <li key={i}><code>{w.cert_id || w.person_id}</code>: {w.reason}</li>
            ))}
          </ul>
        </details>
      )}
      {errors.length > 0 && (
        <details open>
          <summary style={{ cursor: 'pointer', color: '#cc0000' }}>Errors ({errors.length})</summary>
          <ul>
            {errors.map((e, i) => (
              <li key={i}>Row {e.row || e.person_id || i + 1}: {e.reason}</li>
            ))}
          </ul>
        </details>
      )}
    </div>
  )
}
