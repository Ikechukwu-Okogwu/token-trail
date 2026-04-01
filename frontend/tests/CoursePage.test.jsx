import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import '@testing-library/jest-dom/vitest'

vi.mock('../src/services/api', () => ({
  apiFetch: vi.fn(),
}))

vi.mock('../src/components/Sidebar/Sidebar.jsx', () => ({
  default: () => 'Sidebar',
}))

import CoursePage from '../src/pages/CoursePage.jsx'
import { apiFetch } from '../src/services/api'

const assignments = [
  {
    id: 'assign-1',
    title: 'Assignment 1',
    dueDate: '2026-04-15',
    language: 'java',
    isOpen: true,
    submissionCount: 12,
    analysisProgress: 80,
  },
  {
    id: 'assign-2',
    title: 'Assignment 2',
    dueDate: '2026-04-20',
    language: 'C',
    isOpen: false,
    submissionCount: 4,
    analysisProgress: null,
  },
]

const renderCoursePage = () =>
  render(
    <MemoryRouter initialEntries={['/course/course-1']}>
      <Routes>
        <Route path="/course/:courseId" element={<CoursePage onAssignmentCreated={vi.fn()} />} />
      </Routes>
    </MemoryRouter>,
    { legacyRoot: true }
  )

describe('CoursePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiFetch.mockResolvedValue(assignments)
  })

  it('shows loading state then renders assignment cards', async () => {
    renderCoursePage()

    const page = screen.getAllByRole('main')[0]
    expect(within(page).getByText(/loading assignments/i)).toBeInTheDocument()

    expect(await within(page).findByText('Assignment 1')).toBeInTheDocument()
    expect(within(page).getByText('Assignment 2')).toBeInTheDocument()
    expect(within(page).getByText('Due: 2026-04-15')).toBeInTheDocument()
    expect(within(page).getByText('80%')).toBeInTheDocument()
  })

  it('filters assignments using the search input', async () => {
    const user = userEvent.setup()
    renderCoursePage()

    const page = screen.getAllByRole('main')[0]
    expect(await within(page).findByText('Assignment 1')).toBeInTheDocument()

    const searchInput = within(page).getByPlaceholderText('Search assignments…')
    await user.type(searchInput, 'Assignment 2', { delay: null })

    await waitFor(() => {
      expect(within(page).getByText('Assignment 2')).toBeInTheDocument()
      expect(within(page).queryByText('Assignment 1')).not.toBeInTheDocument()
    })
  })

  it('opens the create assignment modal when New is clicked', async () => {
    const user = userEvent.setup()
    renderCoursePage()

    const page = screen.getAllByRole('main')[0]

    await user.click(within(page).getByRole('button', { name: /new/i }))

    expect(screen.getByRole('heading', { name: /new assignment/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create/i })).toBeInTheDocument()
  })

  it('shows course settings when the settings tab is selected', async () => {
    const user = userEvent.setup()
    renderCoursePage()

    const page = screen.getAllByRole('main')[0]

    await user.click(within(page).getByRole('button', { name: /course settings/i }))

    expect(within(page).getByRole('button', { name: /course settings/i })).toHaveClass('bg-[#3b3660]')
  })

  it('renders an error message when the assignment fetch fails', async () => {
    apiFetch.mockRejectedValueOnce(new Error('API failure'))
    renderCoursePage()

    expect(await screen.findByText('API failure')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
  })
})
