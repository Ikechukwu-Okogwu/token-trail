import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

// Mock API module
vi.mock('../src/services/api', () => ({
  getCourseAssignments: vi.fn(),
  getInstructorCourses: vi.fn(),
}))

import Sidebar from '../src/components/Sidebar/Sidebar.jsx'
import { getCourseAssignments, getInstructorCourses } from '../src/services/api'

describe('Sidebar component', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    // Fresh localStorage mock
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

    // IMPORTANT: only resolve ONCE per test
    getInstructorCourses.mockResolvedValue([
      {
        id: 'course-1',
        name: 'COSC 4P02',
        assignments: [
          { id: 'a1', title: 'Assignment 1' },
          { id: 'a2', title: 'Assignment 2' },
        ],
      },
      {
        id: 'course-2',
        name: 'COSC 4P01',
        assignments: [{ id: 'a1', title: 'Assignment 1' }],
      },
    ])

    getCourseAssignments.mockResolvedValue([
      {
        id: 'a3',
        title: 'Assignment 3 (from API)',
      },
    ])
  })

  it('renders static links and courses', async () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Sidebar />
      </MemoryRouter>,
      { legacyRoot: true }
    )

    // Wait for async data to load
    await screen.findByText('COSC 4P02')

    expect(screen.getByText('Token Trail')).toBeTruthy()
    expect(screen.getByText('Home')).toBeTruthy()
    expect(screen.getByText('COSC 4P02')).toBeTruthy()
    expect(screen.getByText('COSC 4P01')).toBeTruthy()
    expect(screen.getByAltText('Account')).toBeTruthy()
    expect(screen.getByAltText('Notifications')).toBeTruthy()
  })

  // it('toggles course expansion and calls getCourseAssignments', async () => {
  //   render(
  //     <MemoryRouter initialEntries={['/dashboard']}>
  //       <Sidebar />
  //     </MemoryRouter>,
  //     { legacyRoot: true }
  //   )

  //   // Ensure DOM is stable first
  //   await screen.findByText('COSC 4P02')

  //   const expanderButton = screen.getByRole('button', {
  //     name: /toggle cosc 4p02/i
  //   })

  //   fireEvent.click(expanderButton)

  //   await waitFor(() => {
  //     expect(screen.getByText('Assignment 1')).toBeTruthy()
  //     expect(screen.getByText('Assignment 2')).toBeTruthy()
  //   })

  //   expect(getCourseAssignments).toHaveBeenCalledTimes(1)
  //   expect(getCourseAssignments).toHaveBeenCalledWith('course-1')
  // })

  it('auto-expands course when route contains assignment path', async () => {
    render(
      <MemoryRouter initialEntries={['/course/course-1/assignment/a1']}>
        <Sidebar />
      </MemoryRouter>,
      { legacyRoot: true }
    )

    await waitFor(() => {
      expect(screen.getByText('Assignment 1')).toBeTruthy()
      expect(screen.getByText('Assignment 2')).toBeTruthy()
    })
  })
})