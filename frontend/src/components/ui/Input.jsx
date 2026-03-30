/**
 * Input — consistent text/email/password input field with label.
 */
export default function Input({ label, id, error, className = '', ...props }) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`w-full border border-gray-300 rounded-xl px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400
          focus:outline-none focus:ring-2 focus:ring-[#3b3660]/20 focus:border-[#3b3660]
          disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed
          read-only:bg-gray-50 read-only:text-gray-500
          ${error ? 'border-red-400 focus:border-red-400 focus:ring-red-200' : ''}
          ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  )
}
