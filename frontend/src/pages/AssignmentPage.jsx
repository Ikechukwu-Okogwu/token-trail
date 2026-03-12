import { Link, useParams } from 'react-router-dom'
import Sidebar from '../components/Sidebar/Sidebar'
import { DUMMY_SUBMISSION_ID } from '../constants/submissionComparison'

export default function AssignmentPage({ courses = [] }) {
  const { courseId, assignmentId } = useParams()
  const comparisonUrl =
    courseId && assignmentId
      ? `/course/${courseId}/assignment/${assignmentId}/submission/${DUMMY_SUBMISSION_ID}`
      : null

  return (
    <div className="h-screen flex">
      <Sidebar courses={courses} />
      <main className="ml-55 flex-1 overflow-auto p-6">
        <h2>Assignment page</h2>
        {comparisonUrl && (
          <Link
            to={comparisonUrl}
            className="text-brand-purple hover:underline mt-2 inline-block"
          >
            View submission comparison
          </Link>
        )}
      </main>
    </div>
  )
}