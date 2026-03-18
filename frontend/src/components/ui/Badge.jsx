/**
 * Badge — status pill for analysis runs and similarity scores.
 *
 * status variant:  queued | running | completed | failed
 * score variant:   pass score (0-1) to get colour-coded score pill
 */
const statusStyles = {
  queued:    'bg-amber-50 text-amber-700 border border-amber-200',
  running:   'bg-blue-50 text-blue-700 border border-blue-200',
  completed: 'bg-green-50 text-green-700 border border-green-200',
  failed:    'bg-red-50 text-red-700 border border-red-200',
  default:   'bg-gray-100 text-gray-600 border border-gray-200',
}

export function StatusBadge({ status }) {
  const s = (status || '').toLowerCase()
  const cls = statusStyles[s] || statusStyles.default
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${cls}`}>
      {s === 'running' && (
        <span className="mr-1.5 w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
      )}
      {(status || 'unknown').toUpperCase()}
    </span>
  )
}

export function ScoreBadge({ score }) {
  const pct = score * 100
  let cls = 'bg-green-50 text-green-700 border border-green-200'
  if (pct >= 80) cls = 'bg-red-50 text-red-600 border border-red-200'
  else if (pct >= 50) cls = 'bg-amber-50 text-amber-700 border border-amber-200'
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold tabular-nums ${cls}`}>
      {pct.toFixed(1)}%
    </span>
  )
}
