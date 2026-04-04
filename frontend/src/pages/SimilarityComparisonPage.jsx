import { useEffect, useState, useRef, useCallback, forwardRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getSimilarityComparison } from '../services/api'
import Sidebar from '../components/Sidebar/Sidebar'
import ErrorBanner from '../components/ui/ErrorBanner'
import { DarkWarningBanner } from '../components/ui/WarningBanner'
import {
  ArrowLeft, Info, User, FileCode, Loader2,
  ChevronLeft, ChevronRight, Crosshair, Shield,
  Moon, Sun
} from 'lucide-react'

function truncateId(value) {
  if (!value) return value
  return value.length > 16 ? value.slice(0, 8) + '…' : value
}

/* ─── Score helpers ─── */

function scoreMeta(score) {
  const pct = Math.round(score * 100)
  if (pct >= 90) return { pct, color: 'text-red-400', bg: 'bg-red-500', ringColor: 'ring-red-500/30', badgeCls: 'bg-red-900/40 text-red-400 border-red-800', label: 'Very High Overlap' }
  if (pct >= 70) return { pct, color: 'text-red-400', bg: 'bg-red-500', ringColor: 'ring-red-500/30', badgeCls: 'bg-red-900/40 text-red-400 border-red-800', label: 'High Overlap' }
  if (pct >= 50) return { pct, color: 'text-amber-400', bg: 'bg-amber-400', ringColor: 'ring-amber-400/30', badgeCls: 'bg-amber-900/40 text-amber-400 border-amber-800', label: 'Moderate Overlap' }
  if (pct >= 30) return { pct, color: 'text-yellow-400', bg: 'bg-yellow-400', ringColor: 'ring-yellow-400/30', badgeCls: 'bg-yellow-900/40 text-yellow-400 border-yellow-800', label: 'Low Overlap' }
  return { pct, color: 'text-green-400', bg: 'bg-green-500', ringColor: 'ring-green-500/30', badgeCls: 'bg-green-900/40 text-green-400 border-green-800', label: 'Minimal Overlap' }
}

function buildLineHighlightMap(regions, side, activeIdx) {
  const map = {}
  if (!regions) return map
  regions.forEach((region, rIdx) => {
    const startKey = side === 'left' ? 'leftStartLine' : 'rightStartLine'
    const endKey = side === 'left' ? 'leftEndLine' : 'rightEndLine'
    const start = region[startKey]
    const end = region[endKey]
    if (start == null || end == null) return
    for (let line = start; line <= end; line++) {
      map[line] = { regionIdx: rIdx, isActive: rIdx === activeIdx }
    }
  })
  return map
}

/* ─── Main page ─── */

export default function SimilarityComparisonPage() {
  const { runId, resultId } = useParams()
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [activeMatch, setActiveMatch] = useState(0)
  const [showOnlyMatches, setShowOnlyMatches] = useState(false)
  const [theme, setTheme] = useState('light')

  const leftPaneRef = useRef(null)
  const rightPaneRef = useRef(null)

  useEffect(() => {
    setLoading(true)
    getSimilarityComparison(decodeURIComponent(resultId))
      .then(setData)
      .catch((err) => setError(err.message || 'Failed to load comparison.'))
      .finally(() => setLoading(false))
  }, [resultId])

  const regions = data?.matchingRegions || []
  const meta = data ? scoreMeta(data.similarityScore) : null

  const scrollToMatch = useCallback((idx) => {
    if (!regions[idx]) return
    setActiveMatch(idx)
    const region = regions[idx]

    const scrollPane = (paneRef, lineNum) => {
      if (!paneRef.current) return
      const row = paneRef.current.querySelector(`[data-line="${lineNum}"]`)
      if (row) {
        row.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
    scrollPane(leftPaneRef, region.leftStartLine)
    scrollPane(rightPaneRef, region.rightStartLine)
  }, [regions])

  function handlePrev() {
    const next = activeMatch > 0 ? activeMatch - 1 : regions.length - 1
    scrollToMatch(next)
  }
  function handleNext() {
    const next = activeMatch < regions.length - 1 ? activeMatch + 1 : 0
    scrollToMatch(next)
  }

  const leftHighlights = buildLineHighlightMap(regions, 'left', activeMatch)
  const rightHighlights = buildLineHighlightMap(regions, 'right', activeMatch)

  const isDark = theme === 'dark'
  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light')

  return (
    <div className="h-screen flex">
      <Sidebar />
      <main className={`ml-55 flex-1 flex flex-col overflow-hidden ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>

        {/* ── Top bar ── */}
        <div className={`flex-shrink-0 border-b ${isDark ? 'border-gray-800 bg-gray-900/90' : 'border-gray-200 bg-white/90'} backdrop-blur-sm px-5 py-3`}>
          <div className="flex items-center gap-4">
            <Link
              to={`/similarity/${runId}`}
              className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs transition no-underline ${isDark ? 'text-gray-400 hover:bg-gray-800 hover:text-gray-200' : 'text-gray-600 hover:bg-gray-200 hover:text-gray-800'}`}
            >
              <ArrowLeft className="h-3.5 w-3.5" /> Results
            </Link>

            <div className={`h-4 w-px ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`} />

            <div className="flex items-center gap-2">
              <Crosshair className="h-4 w-4 text-brand-purple" />
              <span className={`text-sm font-semibold ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>Code Comparison</span>
            </div>

            {/* Score section */}
            {data && (
              <div className="ml-auto flex items-center gap-3">
                <button
                  onClick={toggleTheme}
                  className={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs transition ${isDark ? 'border-gray-700 bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white' : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-200 hover:text-gray-900'}`}
                >
                  {isDark ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
                  {isDark ? 'Light' : 'Dark'}
                </button>

                <div className={`flex items-center gap-3 rounded-xl border ${isDark ? 'border-gray-700 bg-gray-800/80' : 'border-gray-300 bg-white/80'} px-4 py-2 ring-1 ${meta.ringColor}`}>
                  <div className="text-center">
                    <div className={`text-2xl font-black tabular-nums leading-none ${meta.color}`}>
                      {meta.pct}%
                    </div>
                    <div className={`mt-0.5 text-[10px] uppercase tracking-wider ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>Similarity</div>
                  </div>
                  <div className="h-8 w-px bg-gray-700" />
                  <div>
                    <div className={`flex h-1.5 w-20 overflow-hidden rounded-full ${isDark ? 'bg-gray-700' : 'bg-gray-300'}`}>
                      <div
                        className={`h-full rounded-full transition-all ${meta.bg}`}
                        style={{ width: `${meta.pct}%` }}
                      />
                    </div>
                    <div className={`mt-1 text-xs font-semibold ${meta.color}`}>{meta.label}</div>
                  </div>
                </div>

                {data.confidence != null && (
                  <div className={`flex items-center gap-1.5 rounded-lg border ${isDark ? 'border-gray-700 bg-gray-800/60' : 'border-gray-300 bg-gray-100/60'} px-3 py-1.5`}>
                    <Shield className="h-3.5 w-3.5 text-gray-500" />
                    <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                      {Math.round(data.confidence * 100)}% confidence
                    </span>
                  </div>
                )}

                {data.analysisMethod && (
                  <div className={`flex items-center gap-1.5 rounded-lg border ${isDark ? 'border-gray-700 bg-gray-800/60' : 'border-gray-300 bg-gray-100/60'} px-2.5 py-1.5`}>
                    <span className={`text-[10px] uppercase tracking-wider ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>Method</span>
                    <span className={`text-xs font-semibold ${
                      data.analysisMethod === 'error_fallback' ? 'text-amber-400' : (isDark ? 'text-gray-300' : 'text-gray-800')
                    }`}>
                      {data.analysisMethod === 'tokenize' ? 'AST Token' : data.analysisMethod === 'error_fallback' ? 'Fallback' : data.analysisMethod}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* ── Context / explanation layer ── */}
        {data && (
          <div className={`flex-shrink-0 border-b ${isDark ? 'border-gray-800/60 bg-gray-900/50' : 'border-gray-200/60 bg-gray-100/50'} px-5 py-2`}>
            <p className="text-xs leading-relaxed">
              <span className={isDark ? 'text-gray-400' : 'text-gray-700'}>
                {data.summary || `Detected ${regions.length} matched block(s) across both submissions.`}
              </span>
              {' · '}
              Highlighted regions indicate structural similarity based on token-level analysis.
            </p>
          </div>
        )}

        {/* ── Warnings banner ── */}
        {data?.warnings?.length > 0 && (
          <DarkWarningBanner warnings={data.warnings} />
        )}

        {/* ── Match navigation bar ── */}
        {data && regions.length > 0 && (
          <div className={`flex-shrink-0 flex items-center justify-between border-b ${isDark ? 'border-gray-800/60 bg-gray-900/40' : 'border-gray-200/60 bg-gray-100/40'} px-5 py-2`}>
            <div className="flex items-center gap-2">
              <button
                onClick={handlePrev}
                className={`inline-flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs transition ${isDark ? 'border-gray-700 bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white' : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-200 hover:text-gray-900'}`}
              >
                <ChevronLeft className="h-3.5 w-3.5" /> Prev
              </button>
              <span className={`min-w-[90px] text-center text-xs font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Match <span className="text-brand-purple font-bold">{activeMatch + 1}</span> of {regions.length}
              </span>
              <button
                onClick={handleNext}
                className={`inline-flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs transition ${isDark ? 'border-gray-700 bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white' : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-200 hover:text-gray-900'}`}
              >
                Next <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>

            <label className={`flex cursor-pointer items-center gap-1.5 text-xs transition-colors ${isDark ? 'text-gray-500 hover:text-gray-300' : 'text-gray-600 hover:text-gray-800'}`}>
              <input
                type="checkbox"
                checked={showOnlyMatches}
                onChange={() => setShowOnlyMatches(p => !p)}
                className="rounded accent-brand-purple"
              />
              Show only matched regions
            </label>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className={`flex flex-1 items-center justify-center gap-2 text-sm ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>
            <Loader2 className="h-5 w-5 animate-spin" />
            Loading comparison…
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="p-6"><ErrorBanner message={error} /></div>
        )}

        {/* ── Code panes ── */}
        {data && (
          <div className="flex flex-1 overflow-hidden">
            <CodePane
              ref={leftPaneRef}
              side="A"
              studentName={data.leftStudentName}
              studentId={data.leftStudentIdentifier}
              submissionId={data.leftSubmissionId}
              filePath={data.leftFilePath}
              code={data.leftCode}
              highlights={leftHighlights}
              showOnlyMatches={showOnlyMatches}
              isDark={isDark}
            />
            <div className="w-px shrink-0 bg-brand-purple/20" />
            <CodePane
              ref={rightPaneRef}
              side="B"
              studentName={data.rightStudentName}
              studentId={data.rightStudentIdentifier}
              submissionId={data.rightSubmissionId}
              filePath={data.rightFilePath}
              code={data.rightCode}
              highlights={rightHighlights}
              showOnlyMatches={showOnlyMatches}
              isDark={isDark}
            />
          </div>
        )}

        {/* ── Footer disclaimer ── */}
        {data && (
          <div className={`flex-shrink-0 border-t ${isDark ? 'border-gray-800 bg-gray-900/80' : 'border-gray-200 bg-gray-100/80'} px-5 py-2.5`}>
            <div className={`flex items-center gap-2 text-xs ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>
              <Info className="h-3.5 w-3.5 shrink-0 text-amber-500/70" />
              Similarity scores indicate structural overlap between submissions and are not proof of misconduct.
              Review the full context before drawing conclusions.
            </div>
          </div>
        )}
      </main>
    </div>
  )
}


/* ─── Code Pane ─── */

const CodePane = forwardRef(function CodePane(
  { side, studentName, studentId, submissionId, filePath, code, highlights, showOnlyMatches, isDark },
  ref
) {
  const lines = (code || '').split('\n')
  const rawName = filePath ? (filePath.split('/').pop() || filePath) : null
  const fileName = rawName === 'merged.txt' ? null : rawName

  const visibleLines = showOnlyMatches
    ? lines.map((line, i) => ({ line, num: i + 1, visible: Boolean(highlights[i + 1]) }))
    : lines.map((line, i) => ({ line, num: i + 1, visible: true }))

  return (
    <div className="flex flex-1 flex-col overflow-hidden min-w-0">
      {/* Pane header */}
      <div className={`flex-shrink-0 border-b ${isDark ? 'border-gray-800 bg-gray-900' : 'border-gray-200 bg-gray-100'} px-4 py-3`}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 min-w-0">
            <div className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-bold shadow-sm ${
              side === 'A'
                ? 'bg-brand-purple/25 text-brand-purple ring-1 ring-brand-purple/30'
                : 'bg-blue-500/20 text-blue-400 ring-1 ring-blue-500/30'
            }`}>
              {side}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <User className={`h-3.5 w-3.5 shrink-0 ${isDark ? 'text-gray-500' : 'text-gray-600'}`} />
                <span className={`truncate text-sm font-semibold ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                  {truncateId(studentName) || <span className={`italic ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>Unnamed Student</span>}
                </span>
              </div>
              <div className={`mt-0.5 truncate font-mono text-xs ${isDark ? 'text-gray-500' : 'text-gray-600'}`} title={studentId}>
                {truncateId(studentId) || '—'}
              </div>
            </div>
          </div>
          {fileName && (
            <div className={`flex shrink-0 items-center gap-1.5 rounded-lg px-2 py-1 ring-1 ${isDark ? 'bg-gray-800 ring-gray-700' : 'bg-gray-200 ring-gray-300'}`}>
              <FileCode className={`h-3 w-3 ${isDark ? 'text-gray-500' : 'text-gray-600'}`} />
              <span className={`font-mono text-xs ${isDark ? 'text-gray-400' : 'text-gray-700'}`}>{fileName}</span>
            </div>
          )}
        </div>
      </div>

      {/* Code body */}
      {!code ? (
        <div className={`flex flex-1 items-center justify-center text-sm ${isDark ? 'text-gray-600' : 'text-gray-500'}`}>
          No source code available
        </div>
      ) : (
        <div className="flex-1 overflow-auto" ref={ref}>
          <table className="w-full border-collapse font-mono text-xs">
            <tbody>
              {visibleLines.map(({ line, num, visible }) => {
                if (!visible) return null
                const hl = highlights[num]
                let rowCls = isDark ? 'hover:bg-gray-800/60' : 'hover:bg-gray-200/60'
                let gutterExtra = ''
                if (hl) {
                  rowCls = hl.isActive
                    ? (isDark ? 'bg-brand-purple/15 hover:bg-brand-purple/20' : 'bg-brand-purple/10 hover:bg-brand-purple/15')
                    : (isDark ? 'bg-brand-purple/[0.06] hover:bg-brand-purple/10' : 'bg-brand-purple/[0.04] hover:bg-brand-purple/8')
                  gutterExtra = hl.isActive
                    ? 'text-brand-purple border-r-brand-purple'
                    : (isDark ? 'text-brand-purple/60 border-r-brand-purple/40' : 'text-brand-purple/70 border-r-brand-purple/50')
                }

                return (
                  <tr key={num} className={rowCls} data-line={num}>
                    <td className={`w-10 select-none border-r py-px pl-3 pr-3 text-right leading-5 ${isDark ? 'border-gray-800 text-gray-600' : 'border-gray-200 text-gray-500'} ${gutterExtra}`}>
                      {num}
                    </td>
                    <td className={`whitespace-pre py-px pl-4 pr-4 leading-5 ${isDark ? 'text-gray-300' : 'text-gray-800'}`}>
                      {line || ' '}
                    </td>
                  </tr>
                )
              })}
              {showOnlyMatches && !visibleLines.some(l => l.visible) && (
                <tr>
                  <td colSpan={2} className={`py-8 text-center text-sm ${isDark ? 'text-gray-600' : 'text-gray-500'}`}>
                    No matched regions found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
})
