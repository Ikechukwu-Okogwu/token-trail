/**
 * Renders one metric with large value above label and configurable color.
 */
export default function MetricsCard({ value, label, colorClass = 'text-gray-700' }) {
  return (
    <div className="flex flex-col items-center">
      <span className={`text-2xl font-bold ${colorClass}`} aria-hidden="true">
        {value}
      </span>
      <span className="text-sm text-gray-600">{label}</span>
    </div>
  )
}
