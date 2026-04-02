import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, cleanup } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import '@testing-library/jest-dom/vitest'

vi.mock('../src/services/api', () => ({
  getSimilarityComparison: vi.fn(),
}))

vi.mock('../src/components/Sidebar/Sidebar.jsx', () => ({
  default: () => 'Sidebar',
}))

vi.mock('../src/components/ui/ErrorBanner.jsx', () => ({
  default: ({ message }) => `Error: ${message}`,
}))

vi.mock('../src/components/ui/WarningBanner.jsx', () => ({
  DarkWarningBanner: ({ warnings }) => `Warnings: ${warnings.join(', ')}`,
}))

import SimilarityComparisonPage from '../src/pages/SimilarityComparisonPage.jsx'
import { getSimilarityComparison } from '../src/services/api'

const mockComparisonData = {
  leftStudentName: 'Alice',
  leftStudentIdentifier: 'A123',
  leftSubmissionId: 'sub-1',
  leftFilePath: 'main.py',
  leftCode: 'print("hello")\nprint("world")',
  rightStudentName: 'Bob',
  rightStudentIdentifier: 'B456',
  rightSubmissionId: 'sub-2',
  rightFilePath: 'main.py',
  rightCode: 'print("hello")\nprint("world")',
  similarityScore: 0.75,
  confidence: 0.9,
  analysisMethod: 'tokenize',
  summary: 'High similarity detected',
  matchingRegions: [
    {
      leftStartLine: 1,
      leftEndLine: 2,
      rightStartLine: 1,
      rightEndLine: 2,
    },
  ],
  warnings: [],
}

const renderPage = async () => {
  render(
    <MemoryRouter initialEntries={["/similarity/test-run/test-result"]}>
      <SimilarityComparisonPage />
    </MemoryRouter>,
    { legacyRoot: true }
  )
  await waitFor(() => expect(getSimilarityComparison).toHaveBeenCalled())
  await waitFor(() => expect(screen.getByText('75%')).toBeInTheDocument()) // Wait for data to be rendered
}

describe('SimilarityComparisonPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getSimilarityComparison.mockResolvedValue(mockComparisonData)
  })

  afterEach(() => {
    cleanup()
  })

  it('renders with light theme by default', async () => {
    await renderPage()

    // Check that light theme elements are present
    expect(screen.getByText('Dark')).toBeInTheDocument()
    expect(screen.getByText('Code Comparison')).toBeInTheDocument()
  })

  it('toggles to light theme when theme button is clicked', async () => {
    const user = userEvent.setup()
    await renderPage()

    const themeButton = screen.getByRole('button', { name: /dark/i })
    expect(themeButton).toHaveTextContent('Dark')

    await user.click(themeButton)

    expect(themeButton).toHaveTextContent('Light')
    // The button text changes to indicate switching to light mode
  })

  it('toggles back to dark theme when clicked again', async () => {
    const user = userEvent.setup()
    await renderPage()

    const themeButton = screen.getByRole('button', { name: /dark/i })

    // Click to light mode
    await user.click(themeButton)
    expect(themeButton).toHaveTextContent('Light')

    // Click back to dark mode
    await user.click(themeButton)
    expect(themeButton).toHaveTextContent('Dark')
  })

  it('displays comparison data correctly', async () => {
    await renderPage()

    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
    expect(screen.getByText('75%')).toBeInTheDocument()
    expect(screen.getByText('90% confidence')).toBeInTheDocument()
  })

  it('shows match navigation when regions exist', async () => {
    await renderPage()

    expect(screen.getByRole('button', { name: /prev/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument()
  })
})