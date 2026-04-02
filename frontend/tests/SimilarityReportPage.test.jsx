import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, within, cleanup } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import '@testing-library/jest-dom/vitest'

vi.mock('../src/services/api', () => ({
  getSimilarityResults: vi.fn(),
  getAnalysisRunStatus: vi.fn(),
}))

vi.mock('../src/components/Sidebar/Sidebar.jsx', () => ({
  default: () => 'Sidebar',
}))

import SimilarityReportPage from '../src/pages/SimilarityReportPage.jsx'
import { getSimilarityResults, getAnalysisRunStatus } from '../src/services/api'

const mockResults = {
  results: [
    {
      resultId: 'res-1',
      leftStudentName: 'Alice',
      leftStudentIdentifier: 'A123',
      rightStudentName: 'Bob',
      rightStudentIdentifier: 'B456',
      similarityScore: 0.75,
      warnings: [],
    },
  ],
}

const mockRunInfo = {
  courseId: 'course-1',
  assignmentId: 'assignment-1',
  status: 'completed',
}

const renderPage = async () => {
  render(
    <MemoryRouter initialEntries={["/similarity/test-run"]}>
      <SimilarityReportPage />
    </MemoryRouter>,
    { legacyRoot: true }
  )
  await waitFor(() => expect(getSimilarityResults).toHaveBeenCalled())
}

describe('SimilarityReportPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getSimilarityResults.mockResolvedValue(mockResults)
    getAnalysisRunStatus.mockResolvedValue(mockRunInfo)
  })

  afterEach(() => {
    cleanup()
  })

  it('renders with detailed view by default', async () => {
    await renderPage()

    expect(screen.getByRole('button', { name: /compact view/i })).toBeInTheDocument()
    expect(screen.getByText(/A123/)).toBeInTheDocument()
    expect(screen.getByText(/B456/)).toBeInTheDocument()
  })

  it('toggles to compact view and hides identifiers', async () => {
    const user = userEvent.setup()
    await renderPage()

    const [toggle] = screen.getAllByRole('button', { name: /compact view/i })
    await user.click(toggle)

    expect(toggle).toHaveTextContent(/detailed view/i)

    const row = screen.getAllByText('Alice')[0].closest('tr')
    expect(within(row).queryByText(/A123/)).not.toBeInTheDocument()
    expect(within(row).queryByText(/B456/)).not.toBeInTheDocument()
  })

  it('keeps identifiers visible when toggled back to detailed view', async () => {
    const user = userEvent.setup()
    await renderPage()

    const [toggle] = screen.getAllByRole('button', { name: /compact view/i })
    await user.click(toggle)

    const rowCompact = screen.getAllByText('Alice')[0].closest('tr')

    await waitFor(() => {
      expect(toggle).toHaveTextContent(/detailed view/i)
      expect(within(rowCompact).queryByText(/A123/)).not.toBeInTheDocument()
    })

    await user.click(toggle)
    await waitFor(() => {
      expect(toggle).toHaveTextContent(/compact view/i)
      const rowDetailed = screen.getAllByText('Alice')[0].closest('tr')
      expect(within(rowDetailed).getByText(/A123/)).toBeInTheDocument()
      expect(within(rowDetailed).getByText(/B456/)).toBeInTheDocument()
    })
  })
})
