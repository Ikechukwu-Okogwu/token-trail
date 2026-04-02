import { AlertTriangle } from 'lucide-react'

/**
 * Collapsible warning banner for analysis diagnostics.
 * Shows nothing if warnings is empty/null.
 */
export default function WarningBanner({ warnings, className = '' }) {
  if (!warnings || warnings.length === 0) return null

  return (
    <div className={`rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 ${className}`}>
      <div className="flex items-start gap-2.5">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-amber-800">
            Analysis Warning{warnings.length > 1 ? 's' : ''}
          </p>
          <ul className="mt-1 space-y-0.5">
            {warnings.map((w, i) => (
              <li key={i} className="text-xs text-amber-700 leading-relaxed">{w}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}


/**
 * Dark-themed warning banner for the comparison page.
 */
export function DarkWarningBanner({ warnings, className = '' }) {
  if (!warnings || warnings.length === 0) return null

  return (
    <div className={`flex items-start gap-2.5 border-b border-amber-900/40 bg-amber-950/40 px-5 py-2.5 ${className}`}>
      <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
      <div className="flex-1 min-w-0">
        <span className="text-xs font-semibold text-amber-400">Warning: </span>
        {warnings.map((w, i) => (
          <span key={i} className="text-xs text-amber-500/80">
            {w}{i < warnings.length - 1 ? ' · ' : ''}
          </span>
        ))}
      </div>
    </div>
  )
}
