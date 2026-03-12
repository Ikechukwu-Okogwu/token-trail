/**
 * List of similarity candidates with percentage + name, color-coded, clickable rows.
 * Sorted descending by similarity; keyboard accessible.
 */
function similarityColorClass(score) {
  if (score >= 70) return 'text-red-600'
  if (score >= 50) return 'text-orange-600'
  if (score >= 30) return 'text-yellow-600'
  return 'text-green-600'
}

export default function SimilarityCandidatesList({ candidates = [], onSelect, selectedResultId }) {
  if (candidates.length === 0) {
    return (
      <div className="p-4 text-gray-500">
        No similarity results for this submission.
      </div>
    )
  }

  return (
    <ul className="divide-y divide-gray-200" role="list">
      {candidates.map((c) => (
        <li key={c.resultId}>
          <button
            type="button"
            onClick={() => onSelect?.(c)}
            className={`w-full text-left px-4 py-2 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-purple-500 ${selectedResultId === c.resultId ? 'bg-gray-100' : ''}`}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                onSelect?.(c)
              }
            }}
          >
            <span className={`font-semibold ${similarityColorClass(c.similarityScore)}`}>
              {Math.round(c.similarityScore)}%
            </span>
            <span className="ml-2 text-gray-700">{c.studentName}</span>
          </button>
        </li>
      ))}
    </ul>
  )
}
