import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Sidebar from '../components/Sidebar/Sidebar'
import MetricsCard from '../components/SubmissionComparison/MetricsCard'
import CodeComparisonPanel from '../components/SubmissionComparison/CodeComparisonPanel'
import SimilarityCandidatesList from '../components/SubmissionComparison/SimilarityCandidatesList'
import {
  DUMMY_STUDENT_DETAILS,
  DUMMY_METRICS,
  DUMMY_SIMILARITY_CANDIDATES,
  DUMMY_FILES,
  DUMMY_CODE_CONTENT,
} from '../constants/submissionComparison'

// TODO: loading state when wired to real API
// TODO: fetch from GET /api/instructor/assignments/{id} and similarity endpoints

export default function SubmissionComparisonPage({ courses = [] }) {
  const { courseId, assignmentId, submissionId } = useParams()
  const [error, setError] = useState(null)

  // Dummy data - replace with API when backend implements
  const studentDetails = DUMMY_STUDENT_DETAILS
  const metrics = DUMMY_METRICS
  const candidates = DUMMY_SIMILARITY_CANDIDATES

  const [leftFile, setLeftFile] = useState(DUMMY_FILES[0] || '')
  const [rightFile, setRightFile] = useState('')
  const [selectedCandidate, setSelectedCandidate] = useState(null)

  const codeSimilarityColor = metrics.codeSimilarity < 75 ? 'text-green-600' : 'text-red-600'

  const backUrl = courseId && assignmentId ? `/course/${courseId}/assignment/${assignmentId}` : '/dashboard'

  if (error) {
    return (
      <div className="h-screen flex">
        <Sidebar courses={courses} />
        <main className="ml-55 flex-1 overflow-auto p-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            <p>{error}</p>
            <Link to={backUrl} className="underline mt-2 inline-block">
              Back to Assignment
            </Link>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="h-screen flex">
      <Sidebar courses={courses} />
      <main className="ml-55 flex-1 overflow-auto p-6 bg-gray-100">
        <Link
          to={backUrl}
          className="text-brand-purple hover:underline mb-4 inline-block"
          aria-label="Back to assignment"
        >
          Back to Assignment
        </Link>

        {/* Top white box */}
        <div className="bg-white rounded-lg shadow p-4 mb-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div>
              <span className="text-sm text-gray-600">Name: </span>
              <span>{studentDetails.name}</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Student #: </span>
              <span>{studentDetails.studentNumber}</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Files: </span>
              <span>{studentDetails.files}</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Submission Date: </span>
              <span>{studentDetails.submissionDate}</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-8">
            <MetricsCard
              value={`${metrics.codeSimilarity}%`}
              label="Code Similarity"
              colorClass={codeSimilarityColor}
            />
            <MetricsCard
              value={metrics.commonFiles}
              label="Common Files"
              colorClass="text-blue-600"
            />
            <MetricsCard
              value={metrics.matchingLines}
              label="Matching Lines"
              colorClass="text-purple-600"
            />
          </div>
        </div>

        {/* Second white box + similarity list */}
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1 bg-white rounded-lg shadow p-4 flex gap-4 min-h-0">
            <CodeComparisonPanel
              label="Select File"
              ariaLabel="Select file for current submission"
              files={DUMMY_FILES}
              selectedFile={leftFile}
              onFileChange={setLeftFile}
              studentName={studentDetails.name}
              codeContent={leftFile ? DUMMY_CODE_CONTENT : null}
            />
            <CodeComparisonPanel
              label="Select File"
              ariaLabel="Select file for comparison target"
              files={selectedCandidate ? DUMMY_FILES : []}
              selectedFile={rightFile}
              onFileChange={setRightFile}
              studentName={selectedCandidate?.studentName}
              codeContent={selectedCandidate ? DUMMY_CODE_CONTENT : null}
              placeholder="Select a submission from the right"
            />
          </div>
          <div className="w-full lg:w-64 shrink-0 bg-white rounded-lg shadow overflow-hidden flex flex-col">
            <h3 className="text-sm font-medium text-gray-700 px-4 py-2 border-b">
              Similarity Candidates
            </h3>
            <div className="overflow-auto flex-1">
              <SimilarityCandidatesList
                candidates={candidates}
                onSelect={(c) => {
                  setSelectedCandidate(c)
                  setRightFile(DUMMY_FILES[0] || '')
                }}
                selectedResultId={selectedCandidate?.resultId}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
