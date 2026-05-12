export default function DaysWarningBadge({ daysRemaining, daysRequired }) {
  if (!daysRemaining || !daysRequired || daysRequired <= daysRemaining) return null
  const shortfall = Math.ceil(daysRequired - daysRemaining)
  return (
    <span
      title={`${daysRequired} days required, ${daysRemaining} remaining`}
      style={{
        display: 'inline-block',
        background: '#fff3cd',
        color: '#856404',
        border: '1px solid #ffc107',
        borderRadius: 4,
        padding: '0.15rem 0.5rem',
        fontSize: '0.8rem',
        fontWeight: 600,
      }}
    >
      ⚠ {shortfall} day{shortfall !== 1 ? 's' : ''} short
    </span>
  )
}
