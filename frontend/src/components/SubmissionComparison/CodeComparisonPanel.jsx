/**
 * File dropdown, student name, scrollable code area (or placeholder).
 */
export default function CodeComparisonPanel({
  label,
  ariaLabel,
  files = [],
  selectedFile,
  onFileChange,
  studentName,
  codeContent,
  placeholder = null,
}) {
  const showPlaceholder = placeholder && !codeContent
  return (
    <div className="flex flex-col flex-1 min-w-0" role="region" aria-label={ariaLabel}>
      <label className="text-sm font-medium text-gray-700 mb-1">{label}</label>
      <select
        value={selectedFile}
        onChange={(e) => onFileChange?.(e.target.value)}
        className="border border-gray-300 rounded px-2 py-1.5 text-sm mb-2"
        aria-label={ariaLabel}
      >
        <option value="">Select File</option>
        {files.map((f) => (
          <option key={f} value={f}>
            {f}
          </option>
        ))}
      </select>
      {studentName && (
        <p className="text-sm text-gray-600 mb-2">{studentName}</p>
      )}
      <div
        className="flex-1 min-h-[200px] max-h-96 overflow-auto bg-gray-50 rounded border border-gray-200 p-3 font-mono text-sm"
        aria-label={codeContent ? `Code content for ${selectedFile || 'selected file'}` : 'Code display area'}
      >
        {showPlaceholder ? (
          <p className="text-gray-500 italic">{placeholder}</p>
        ) : codeContent ? (
          <pre className="whitespace-pre-wrap break-words m-0">{codeContent}</pre>
        ) : (
          <p className="text-gray-500 italic">No file selected</p>
        )}
      </div>
    </div>
  )
}
