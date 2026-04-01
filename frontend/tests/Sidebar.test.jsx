import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import '@testing-library/jest-dom/vitest'

vi.mock('../src/services/api', () => ({
  getCourseAssignments: vi.fn(),
  getInstructorCourses: vi.fn(),
  getAnalysisRunStatus: vi.fn(),
  logout: vi.fn(),
}))

import Sidebar from '../src/components/Sidebar/Sidebar.jsx'
import { getCourseAssignments, getInstructorCourses, getAnalysisRunStatus } from '../src/services/api'

const mockCourses = [
  { id: 'course-1', name: 'COSC 4P02', term: 'Winter 2026' },
  { id: 'course-2', name: 'COSC 4P01', term: 'Fall 2025' },
]

const mockAssignmentsCourse1 = [
  { id: 'a1', title: 'Assignment 1' },
  { id: 'a2', title: 'Assignment 2' },
]

const mockAssignmentsCourse2 = [
  { id: 'a3', title: 'Assignment 3' },
]

const mockAnalysisRunStatus = {
  courseId: 'course-1',
  assignmentId: 'a2',
}

const renderSidebar = ({ initialEntries = ['/dashboard'] } = {}) =>
  render(
    <MemoryRouter initialEntries={initialEntries}>
      <Sidebar />
    </MemoryRouter>,
    { legacyRoot: true }
  )

describe('Sidebar component', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(() => 'fake-token'),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
      writable: true,
      configurable: true,
    })

    getInstructorCourses.mockResolvedValue(mockCourses)
    getCourseAssignments.mockImplementation((courseId) => {
      if (courseId === 'course-1') return Promise.resolve(mockAssignmentsCourse1)
      if (courseId === 'course-2') return Promise.resolve(mockAssignmentsCourse2)
      return Promise.resolve([])
    })
    getAnalysisRunStatus.mockResolvedValue(mockAnalysisRunStatus)
  })

  it('renders navigation links and course list', async () => {
    renderSidebar()

    expect(await screen.findByText('COSC 4P02')).toBeInTheDocument()
    expect(screen.getByText('Token Trail')).toBeInTheDocument()
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('COSC 4P01')).toBeInTheDocument()
  })

  it('opens a course when its toggle button is clicked and fetches assignments', async () => {
    const user = userEvent.setup()
    renderSidebar()
    const sidebar = screen.getAllByRole('complementary')[0]

    const courseListItem = await within(sidebar).findByText('COSC 4P02')
    const toggleButton = within(courseListItem.closest('li')).getByRole('button')

    expect(toggleButton).toHaveAttribute('aria-expanded', 'false')

    await user.click(toggleButton)

    await waitFor(() => expect(toggleButton).toHaveAttribute('aria-expanded', 'true'))
    expect(getCourseAssignments).toHaveBeenCalledTimes(1)
    expect(getCourseAssignments).toHaveBeenCalledWith('course-1')
    
    expect(await within(sidebar).findByText('Assignment 1')).toBeInTheDocument()
    expect(within(sidebar).getByText('Assignment 2')).toBeInTheDocument()
  })

  it('auto-expands the active course when the route contains an assignment path', async () => {
    renderSidebar({ initialEntries: ['/course/course-1/assignment/a1'] })
    const sidebar = screen.getAllByRole('complementary')[0]

    expect(await within(sidebar).findByText('Assignment 1')).toBeInTheDocument()
    expect(within(sidebar).getByText('Assignment 2')).toBeInTheDocument()
    expect(getCourseAssignments).toHaveBeenCalledWith('course-1')

    const courseListItem = screen.getAllByText('COSC 4P02')[0].closest('li')
    const toggleButton = within(courseListItem).getByRole('button')
    expect(toggleButton).toHaveAttribute('aria-expanded', 'true')
  })

  it('fetches run status and opens the course when runId is present', async () => {
    render(
      <MemoryRouter initialEntries={['/similarity/run-123']}>
        <Routes>
          <Route path="/similarity/:runId" element={<Sidebar />} />
        </Routes>
      </MemoryRouter>,
      { legacyRoot: true }
    )
    const sidebar = screen.getAllByRole('complementary')[0]

    await waitFor(() => expect(getAnalysisRunStatus).toHaveBeenCalledWith('run-123'))

    const assignments = await within(sidebar).findByText('Assignment 2')

    await waitFor(() => {
      const assignmentLink = assignments.closest('a')
      expect(assignmentLink).toBeInTheDocument()
    })
    
  })
})