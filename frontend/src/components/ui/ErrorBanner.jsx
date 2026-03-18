/**
 * ErrorBanner — consistent red error block.
 * Shows message + optional retry button.
 */
export default function ErrorBanner({ message, onRetry }) {
  if (!message) return null
  return (
    <div className="flex items-start gap-3 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
      <svg className="flex-shrink-0 mt-0.5 w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
      </svg>
      <span className="flex-1">{message}</span>
      {onRetry && (
        <button onClick={onRetry} className="ml-2 underline font-medium hover:text-red-900 flex-shrink-0">
          Retry
        </button>
      )}
    </div>
  )
}
