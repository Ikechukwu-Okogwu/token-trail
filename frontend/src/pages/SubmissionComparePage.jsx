import { useState, useEffect } from 'react'
import { apiFetch } from '../services/api'

/**
 * SubmissionComparePage
 * Props:
 *   submissionId: string
 *   assignmentId: string
 *   onBack: () => void
 */
export default function SubmissionComparePage({ submissionId, assignmentId, onBack }) {
  const [submission, setSubmission] = useState(null)
  const [similarityResults, setSimilarityResults] = useState([])
  const [selectedLeftFile, setSelectedLeftFile] = useState('Main.java')
  const [selectedRightSub, setSelectedRightSub] = useState(null)
  const [selectedRightFile, setSelectedRightFile] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch(`/instructor/assignments/${assignmentId}/submissions`)
      .then((subs) => {
        const sub = subs.find((s) => s.submissionId === submissionId)
        setSubmission(sub || null)
        const others = subs
          .filter((s) => s.submissionId !== submissionId)
          .map((s, i) => ({
            submissionId: s.submissionId,
            studentName: s.studentName || s.studentIdentifier,
            // Mock % for UI demo — real data comes from analysis run results
            pct: [72, 70, 66, 53, 41, 40, 38, 38, 14][i] ?? null,
          }))
        setSimilarityResults(others)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [submissionId, assignmentId])

  if (loading) return <div className="p-6 text-gray-400">Loading…</div>
  if (!submission) return <div className="p-6 text-gray-400">Submission not found.</div>

  const leftFiles = ['Main.java', 'Helper.java', 'Node.java']
  const rightFiles = selectedRightSub ? ['Main.java', 'Helper.java'] : []

  // Colour by % threshold
  function pctColor(pct) {
    if (pct == null) return 'text-gray-400'
    if (pct >= 60) return 'text-red-500'
    if (pct >= 40) return 'text-orange-500'
    if (pct >= 20) return 'text-yellow-500'
    return 'text-green-500'
  }

  const selectedResultName = similarityResults.find(
    (r) => r.submissionId === selectedRightSub
  )?.studentName ?? '[student name]'

  return (
    <div className="flex flex-col h-full overflow-hidden">

      {/* ── Top header bar ── */}
      <div className="bg-white border-b border-gray-100 px-6 py-4 flex-shrink-0">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 mb-3 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Back
        </button>
        <div className="flex items-center gap-8 text-sm text-gray-700">
          <span><strong className="font-semibold">Name:</strong> {submission.studentName ?? submission.studentIdentifier}</span>
          <span><strong className="font-semibold">Student #:</strong> {submission.studentIdentifier}</span>
          <span><strong className="font-semibold">Files:</strong> {submission.fileCount}</span>
          <span><strong className="font-semibold">Submission Date:</strong> {submission.submittedAt}</span>
        </div>
      </div>

      {/* ── Body ── */}
      <div className="flex flex-1 overflow-hidden p-5 gap-4">

        {/* Left: stats + code panels */}
        <div className="flex-1 flex flex-col gap-4 overflow-hidden">

          {/* Stat cards */}
          <div className="flex gap-3 flex-shrink-0">
            <div className="flex-1 bg-green-50 border border-green-100 rounded-2xl px-6 py-4 text-center">
              <div className="text-3xl font-bold text-green-500">73%</div>
              <div className="text-xs text-gray-500 mt-1">Code Similarity</div>
            </div>
            <div className="flex-1 bg-blue-50 border border-blue-100 rounded-2xl px-6 py-4 text-center">
              <div className="text-3xl font-bold text-blue-500">4</div>
              <div className="text-xs text-gray-500 mt-1">Common Files</div>
            </div>
            <div className="flex-1 bg-purple-50 border border-purple-100 rounded-2xl px-6 py-4 text-center">
              <div className="text-3xl font-bold text-purple-500">142</div>
              <div className="text-xs text-gray-500 mt-1">Matching Lines</div>
            </div>
          </div>

          {/* Code panels */}
          <div className="flex-1 bg-white rounded-2xl border border-gray-100 overflow-hidden flex">

            {/* Left panel */}
            <div className="flex-1 flex flex-col border-r border-gray-100 overflow-hidden">
              <div className="px-4 pt-4 pb-3 flex-shrink-0">
                <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                  {submission.studentName ?? submission.studentIdentifier}
                </div>
                <div className="text-xs font-medium text-gray-600 mb-2">Select File</div>
                <div className="relative">
                  <select
                    value={selectedLeftFile}
                    onChange={(e) => setSelectedLeftFile(e.target.value)}
                    className="w-full appearance-none border border-gray-200 rounded-xl px-3 py-2 text-sm pr-8 focus:outline-none focus:ring-2 focus:ring-[#3b3660]/30"
                  >
                    {leftFiles.map((f) => <option key={f} value={f}>{f}</option>)}
                  </select>
                  <svg className="absolute right-2.5 top-2.5 w-4 h-4 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7"/>
                  </svg>
                </div>
              </div>
              <div className="flex-1 overflow-auto bg-[#1e1e2e] mx-4 mb-4 rounded-xl">
                <pre className="p-4 text-[12px] font-mono text-[#cdd6f4] leading-relaxed whitespace-pre-wrap">{`import java.util.*;

public class MiniDungeon {

    public static void main(String[] args) {
        Random rand = new Random();
        Scanner sc = new Scanner(System.in);

        String[] rooms = {"Hall", "Armory",
        "Library", "Dungeon", "Garden", "Tower"};
        String[] monsters = {"Goblin", "Skeleton",
        "Mage", "Spider"};
        String[] items = {"potion", "shield",
        "scroll", "ring"};

        int playerHp = 20;
        List<String> inventory = new ArrayList<>();
        String position =
        rooms[rand.nextInt(rooms.length)];

        System.out.println("Welcome to the Mini Dungeon!");
        System.out.println("Type: move, search, rest, or quit");
    }
}`}</pre>
              </div>
            </div>

            {/* Right panel */}
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="px-4 pt-4 pb-3 flex-shrink-0">
                <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                  {selectedResultName}
                </div>
                <div className="text-xs font-medium text-gray-600 mb-2">Select File</div>
                <div className="relative">
                  <select
                    value={selectedRightFile}
                    onChange={(e) => setSelectedRightFile(e.target.value)}
                    disabled={!selectedRightSub}
                    className="w-full appearance-none border border-gray-200 rounded-xl px-3 py-2 text-sm pr-8 focus:outline-none focus:ring-2 focus:ring-[#3b3660]/30 disabled:opacity-50"
                  >
                    <option value="">Select</option>
                    {rightFiles.map((f) => <option key={f} value={f}>{f}</option>)}
                  </select>
                  <svg className="absolute right-2.5 top-2.5 w-4 h-4 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7"/>
                  </svg>
                </div>
              </div>
              <div className="flex-1 overflow-auto bg-gray-100 mx-4 mb-4 rounded-xl flex items-center justify-center">
                {selectedRightSub && selectedRightFile ? (
                  <pre className="p-4 text-[12px] font-mono text-gray-600 leading-relaxed w-full h-full">
                    {`// ${selectedRightFile}\n// Code will load from API`}
                  </pre>
                ) : (
                  <p className="text-sm text-gray-400 text-center px-4 leading-relaxed">
                    Select a submission<br/>from the right to compare
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right: Similar Submissions sidebar */}
        <div className="w-44 flex-shrink-0 bg-white rounded-2xl border border-gray-100 overflow-hidden flex flex-col">
          <div className="px-4 py-3 border-b border-gray-100 flex-shrink-0">
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wide">Similar Submissions</h4>
          </div>
          <div className="flex-1 overflow-y-auto py-2">
            {similarityResults.map((r) => (
              <button
                key={r.submissionId}
                onClick={() => setSelectedRightSub(r.submissionId)}
                className={`flex items-center gap-2 w-full px-4 py-2.5 text-left hover:bg-gray-50 transition-colors
                  ${selectedRightSub === r.submissionId ? 'bg-gray-50' : ''}`}
              >
                <span className={`text-sm font-bold min-w-[38px] ${pctColor(r.pct)}`}>
                  {r.pct != null ? `${r.pct}%` : '--%'}
                </span>
                <span className="text-xs text-gray-600 truncate">{r.studentName}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
