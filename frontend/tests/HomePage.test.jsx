import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import '@testing-library/jest-dom/vitest'

vi.mock('../src/services/api', () => ({
  apiFetch: vi.fn(),
}))

vi.mock('../src/components/Sidebar/Sidebar.jsx', () => ({
  default: () => 'Sidebar',
}))

import HomePage from '../src/pages/HomePage.jsx'
import { apiFetch } from '../src/services/api'

const mockCourses = [
  {
    id: 'course-1',
    name: 'COSC 4P02',
    term: 'Winter 2026',
    assignmentCount: 3,
    analysisCompleteCount: 1,
  },
  {
    id: 'course-2',
    name: 'COSC 4P01',
    term: 'Fall 2025',
    assignmentCount: 1,
    analysisCompleteCount: 0,
  },
]

const renderHomePage = (props = {}) =>
  render(
    <MemoryRouter>
      <HomePage onCourseCreated={vi.fn()} onLogout={vi.fn()} {...props} />
    </MemoryRouter>,
    { legacyRoot: true }
  )

describe('HomePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiFetch.mockResolvedValue(mockCourses)
  })
  
  it('shows loading state then renders course cards', async () => {
    renderHomePage()
    const courseGrid = screen.getAllByRole('main')[0]

    expect(within(courseGrid).getByText(/loading courses/i)).toBeInTheDocument()

    expect(await within(courseGrid).findByText('COSC 4P02')).toBeInTheDocument()
    expect(within(courseGrid).getByText('Winter 2026')).toBeInTheDocument()
    expect(within(courseGrid).getByText('COSC 4P01')).toBeInTheDocument()
  })

  it('filters courses using the search input', async () => {
    const user = userEvent.setup()
    renderHomePage()
    const courseGrid = screen.getAllByRole('main')[0]

    expect(await within(courseGrid).findByText('COSC 4P02')).toBeInTheDocument()

    const searchInput = within(courseGrid).getByPlaceholderText('Search courses…')
    await user.type(searchInput, '4P01', {delay: null})

    await waitFor(() => {
      expect(within(courseGrid).getByText('COSC 4P01')).toBeInTheDocument()
      expect(within(courseGrid).queryByText('COSC 4P02')).not.toBeInTheDocument()
    })
  })

  it('switches to list view when the list button is clicked', async () => {
    const user = userEvent.setup()
    renderHomePage()
    const courseGrid = screen.getAllByRole('main')[0]

    await waitFor(() => {
      expect(within(courseGrid).queryByText(/loading courses/i)).not.toBeInTheDocument()
    })

    const listViewButton = within(courseGrid).getByRole('button', { name: /list view/i })
    await user.click(listViewButton)

    expect(listViewButton).toHaveClass('bg-white')
    expect(within(courseGrid).getByText('COSC 4P01')).toBeInTheDocument()
  })

  it('opens the create course modal when New is clicked', async () => {
    const user = userEvent.setup()
    renderHomePage()
    const courseGrid = screen.getAllByRole('main')[0]

    await user.click(within(courseGrid).getByRole('button', { name: /new/i }))

    expect(within(courseGrid).getByRole('heading', { name: /new course/i })).toBeInTheDocument()
    expect(within(courseGrid).getByRole('button', { name: /create/i })).toBeInTheDocument()
  })

  it('renders an error message when the course fetch fails', async () => {
    apiFetch.mockRejectedValueOnce(new Error('Server is unavailable'))
    renderHomePage()

    expect(await screen.findByText('Server is unavailable')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
  })
})
