/*
Test Plan
- Input partitions: valid assignment ID route param, invalid route param, and blank manual input.
- Boundary values: empty assignment input after clearing the form.
- Interface misuse: malformed route param should not trigger API reads.
- Failure modes: completed-run transition should expose results CTA with correct route.
- Repeated-call behavior: repeated status refresh clicks should repeatedly call status API without breaking state.
*/

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import AssignmentDetailPage from '../AssignmentDetailPage'
import * as api from '../../services/api'

vi.mock('../../services/api', () => ({
  getAnalysisRunStatus: vi.fn(),
  getAssignmentSubmissions: vi.fn(),
  getInstructorAssignmentById: vi.fn(),
  queueAnalysisRun: vi.fn(),
}))

const VALID_ASSIGNMENT_ID = '507f1f77bcf86cd799439011'
const COURSE_ID = 'course-123'

function renderAt(routePath) {
  return render(
    <MemoryRouter initialEntries={[routePath]}>
      <Routes>
        <Route
          path="/course/:courseId/assignment/:assignmentId/details"
          element={<AssignmentDetailPage />}
        />
      </Routes>
    </MemoryRouter>
  )
}

describe('AssignmentDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.getInstructorAssignmentById.mockResolvedValue({
      id: VALID_ASSIGNMENT_ID,
      title: 'Assignment One',
      language: 'python',
      assignmentKey: 'abc123',
      isOpen: true,
      dueDate: '2026-01-01T00:00:00Z',
      keyExpiry: '2026-01-02T00:00:00Z',
      autoAnalysis: true,
      allowLate: false,
      exclusionCode: null,
      createdAt: '2025-12-31T00:00:00Z',
    })
    api.getAssignmentSubmissions.mockResolvedValue([
      {
        submissionId: 'sub-1',
        studentIdentifier: 's12345',
        studentName: 'Alex Student',
        submittedAt: '2026-01-01T12:00:00Z',
        fileCount: 2,
        status: 'submitted',
      },
    ])
    api.queueAnalysisRun.mockResolvedValue({
      runId: 'run-1',
      status: 'queued',
      algorithmVersion: 'v1',
    })
    api.getAnalysisRunStatus.mockResolvedValue({
      runId: 'run-1',
      status: 'running',
      algorithmVersion: 'v1',
      createdAt: '2026-01-01T13:00:00Z',
      startedAt: '2026-01-01T13:01:00Z',
      finishedAt: null,
      errorMessage: null,
    })
  })

  it('loads assignment and submissions from a valid route assignment ID', async () => {
    // Why: validation test that proves the happy-path route param triggers both data APIs and renders loaded content.
    renderAt(`/course/${COURSE_ID}/assignment/${VALID_ASSIGNMENT_ID}/details`)

    expect(await screen.findByText('Assignment One')).toBeInTheDocument()
    expect(screen.getByText('Alex Student')).toBeInTheDocument()
    expect(api.getInstructorAssignmentById).toHaveBeenCalledWith(VALID_ASSIGNMENT_ID)
    expect(api.getAssignmentSubmissions).toHaveBeenCalledWith(VALID_ASSIGNMENT_ID)
    expect(screen.getByRole('button', { name: 'Run Analysis' })).toBeEnabled()
  })

  it('shows route-format guidance and does not call read APIs for malformed route IDs', async () => {
    // Why: defect test that protects against accidental API calls with sample IDs like "a1".
    renderAt(`/course/${COURSE_ID}/assignment/a1/details`)

    expect(
      await screen.findByText(
        'Route assignment ID is not in API format. Enter a valid assignment ID and click Load.'
      )
    ).toBeInTheDocument()
    expect(api.getInstructorAssignmentById).not.toHaveBeenCalled()
    expect(api.getAssignmentSubmissions).not.toHaveBeenCalled()
  })

  it('shows a boundary error for empty assignment input on manual load', async () => {
    // Why: boundary test for empty input so the page guards against blank submissions before network calls.
    const user = userEvent.setup()
    renderAt(`/course/${COURSE_ID}/assignment/a1/details`)

    const input = await screen.findByLabelText('Assignment ID')
    await user.clear(input)
    await user.click(screen.getByRole('button', { name: 'Load' }))

    expect(screen.getByText('Enter an assignment ID first.')).toBeInTheDocument()
    expect(api.getInstructorAssignmentById).not.toHaveBeenCalled()
    expect(api.getAssignmentSubmissions).not.toHaveBeenCalled()
  })

  it('renders View Similarity Results link with course, assignment, and run IDs after completion', async () => {
    // Why: regression test for the new completed-state CTA and route contract required by scrum.
    const user = userEvent.setup()
    api.getAnalysisRunStatus.mockResolvedValueOnce({
      runId: 'run-1',
      status: 'completed',
      algorithmVersion: 'v1',
      createdAt: '2026-01-01T13:00:00Z',
      startedAt: '2026-01-01T13:01:00Z',
      finishedAt: '2026-01-01T13:02:00Z',
      errorMessage: null,
    })

    renderAt(`/course/${COURSE_ID}/assignment/${VALID_ASSIGNMENT_ID}/details`)
    await screen.findByText('Assignment One')

    await user.click(screen.getByRole('button', { name: 'Run Analysis' }))
    await user.click(screen.getByRole('button', { name: 'Refresh Status' }))

    const cta = await screen.findByRole('link', {
      name: 'View Similarity Results',
    })
    expect(cta).toHaveAttribute(
      'href',
      `/course/${COURSE_ID}/assignment/${VALID_ASSIGNMENT_ID}/run/run-1/results`
    )
  })

  it('supports repeated refresh-status calls once a run is queued', async () => {
    // Why: stress/repeated-call test to ensure refresh can be triggered repeatedly without losing behavior.
    const user = userEvent.setup()
    renderAt(`/course/${COURSE_ID}/assignment/${VALID_ASSIGNMENT_ID}/details`)
    await screen.findByText('Assignment One')

    await user.click(screen.getByRole('button', { name: 'Run Analysis' }))

    const refreshButton = screen.getByRole('button', { name: 'Refresh Status' })
    for (let i = 0; i < 5; i += 1) {
      await user.click(refreshButton)
    }

    await waitFor(() => {
      expect(api.getAnalysisRunStatus).toHaveBeenCalledTimes(5)
    })
  })
})
