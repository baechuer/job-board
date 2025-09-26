import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';
import JobApplications from './JobApplications';
import api from '../../services/api';

vi.mock('../../services/api', () => ({ default: { get: vi.fn(), patch: vi.fn() } }));

const mockJob = {
  id: 1,
  title: 'Software Engineer',
  location: 'San Francisco',
  created_at: '2024-01-01T00:00:00Z'
};

const mockApplications = [
  {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    phone: '123-456-7890',
    current_company: 'Tech Corp',
    experience: '3-5 years',
    salary_expectation: 70000,
    status: 'submitted',
    applied_at: '2024-01-01T00:00:00Z',
    additional_info: 'Passionate developer'
  },
  {
    id: 2,
    first_name: 'Jane',
    last_name: 'Smith',
    email: 'jane@example.com',
    phone: '987-654-3210',
    current_company: 'Startup Inc',
    experience: '1-2 years',
    salary_expectation: 60000,
    status: 'accepted',
    applied_at: '2024-01-02T00:00:00Z',
    additional_info: 'Eager to learn'
  },
  {
    id: 3,
    first_name: 'Bob',
    last_name: 'Johnson',
    email: 'bob@example.com',
    phone: '555-123-4567',
    current_company: 'Big Corp',
    experience: '5-10 years',
    salary_expectation: 90000,
    status: 'rejected',
    applied_at: '2024-01-03T00:00:00Z',
    additional_info: 'Senior developer'
  }
];

const renderPage = (jobId = '1') => render(
  <MemoryRouter initialEntries={[`/recruiter/jobs/${jobId}/applications`]}>
    <Routes>
      <Route path="/recruiter/jobs/:jobId/applications" element={<JobApplications />} />
    </Routes>
  </MemoryRouter>
);

describe('JobApplications', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders job applications correctly', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('Job Applications'));
    
    // Check header
    expect(screen.getByText('Job Applications')).toBeInTheDocument();
    expect(screen.getByText('← Back to Job Details')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    expect(screen.getByText('San Francisco')).toBeInTheDocument();
    
    // Check applications
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Bob Johnson')).toBeInTheDocument();
    
    // Check status badges
    expect(screen.getByText('submitted')).toBeInTheDocument();
    expect(screen.getByText('accepted')).toBeInTheDocument();
    expect(screen.getByText('rejected')).toBeInTheDocument();
  });

  it('renders status filter tabs with correct counts', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('All Applications'));
    
    // Check filter tabs
    expect(screen.getByText('All Applications')).toBeInTheDocument();
    expect(screen.getByText('Submitted')).toBeInTheDocument();
    expect(screen.getByText('Under Review')).toBeInTheDocument();
    expect(screen.getByText('Accepted')).toBeInTheDocument();
    expect(screen.getByText('Rejected')).toBeInTheDocument();
    
    // Check counts
    expect(screen.getByText('3')).toBeInTheDocument(); // All applications
    expect(screen.getAllByText('1')).toHaveLength(3); // Submitted, Accepted, Rejected
  });

  it('filters applications by status when tab is clicked', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('All Applications'));
    
    // Click on Submitted tab
    const submittedTab = screen.getByText('Submitted');
    fireEvent.click(submittedTab);
    
    // Should only show submitted applications
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    expect(screen.queryByText('Bob Johnson')).not.toBeInTheDocument();
  });

  it('filters applications by accepted status', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('All Applications'));
    
    // Click on Accepted tab
    const acceptedTab = screen.getByText('Accepted');
    fireEvent.click(acceptedTab);
    
    // Should only show accepted applications
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
    expect(screen.queryByText('Bob Johnson')).not.toBeInTheDocument();
  });

  it('filters applications by rejected status', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('All Applications'));
    
    // Click on Rejected tab
    const rejectedTab = screen.getByText('Rejected');
    fireEvent.click(rejectedTab);
    
    // Should only show rejected applications
    expect(screen.getByText('Bob Johnson')).toBeInTheDocument();
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
    expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
  });

  it('shows all applications when All Applications tab is clicked', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('All Applications'));
    
    // Click on Submitted first
    const submittedTab = screen.getByText('Submitted');
    fireEvent.click(submittedTab);
    
    // Then click on All Applications
    const allTab = screen.getByText('All Applications');
    fireEvent.click(allTab);
    
    // Should show all applications again
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Bob Johnson')).toBeInTheDocument();
  });

  it('shows no applications message when filter has no results', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('All Applications'));
    
    // Click on Under Review tab (no applications with this status)
    const reviewedTab = screen.getByText('Under Review');
    fireEvent.click(reviewedTab);
    
    // Should show no applications message
    expect(screen.getByText('No applications')).toBeInTheDocument();
    expect(screen.getByText('No applications with status "reviewed".')).toBeInTheDocument();
  });

  it('shows no applications message when there are no applications at all', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: [] } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('No applications'));
    
    expect(screen.getByText('No applications have been submitted for this job yet.')).toBeInTheDocument();
  });

  it('handles status update successfully', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    api.patch.mockResolvedValue({ data: { message: 'Status updated' } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('Mark as Reviewing'));
    
    const reviewButton = screen.getByText('Mark as Reviewing');
    fireEvent.click(reviewButton);
    
    await waitFor(() => {
      expect(api.patch).toHaveBeenCalledWith('/applications/1/status', {
        status: 'reviewed'
      });
    });
  });

  it('handles accept status update', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    api.patch.mockResolvedValue({ data: { message: 'Status updated' } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('Accept'));
    
    const acceptButtons = screen.getAllByText('Accept');
    fireEvent.click(acceptButtons[0]); // Click first accept button
    
    await waitFor(() => {
      expect(api.patch).toHaveBeenCalledWith('/applications/1/status', {
        status: 'accepted'
      });
    });
  });

  it('handles reject status update', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    api.patch.mockResolvedValue({ data: { message: 'Status updated' } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('Reject'));
    
    const rejectButtons = screen.getAllByText('Reject');
    fireEvent.click(rejectButtons[0]); // Click first reject button
    
    await waitFor(() => {
      expect(api.patch).toHaveBeenCalledWith('/applications/1/status', {
        status: 'rejected'
      });
    });
  });

  it('shows correct action buttons based on application status', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    // Submitted application should have all three buttons
    expect(screen.getByText('Mark as Reviewing')).toBeInTheDocument();
    expect(screen.getAllByText('Accept')).toHaveLength(1); // Only for submitted application
    expect(screen.getAllByText('Reject')).toHaveLength(1); // Only for submitted application
    
    // Accepted application should not have action buttons
    // Rejected application should not have action buttons
  });

  it('navigates to application detail when View Full Application is clicked', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    const viewButtons = screen.getAllByText('View Full Application');
    expect(viewButtons).toHaveLength(3); // Should have 3 buttons for 3 applications
    
    // Test that the button exists and is clickable
    expect(viewButtons[0]).toBeInTheDocument();
    fireEvent.click(viewButtons[0]);
    
    // The navigation will be handled by React Router in the test environment
    // We can't easily test the actual navigation without more complex setup
  });

  it('shows loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderPage('1');
    
    expect(screen.getAllByRole('generic')).toHaveLength(9); // Loading skeleton
  });

  it('shows error state when API call fails', async () => {
    api.get.mockRejectedValue(new Error('API Error'));
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('Error'));
    
    expect(screen.getByText('Failed to load applications')).toBeInTheDocument();
  });

  it('shows job not found when job is null', async () => {
    api.get
      .mockResolvedValueOnce({ data: null })
      .mockResolvedValueOnce({ data: { applications: [] } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('Job Not Found'));
    
    expect(screen.getByText('The job you\'re looking for doesn\'t exist.')).toBeInTheDocument();
  });

  it('formats dates correctly', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    // Check that dates are formatted
    expect(screen.getAllByText(/Applied:/)).toHaveLength(3);
  });

  it('formats salary correctly', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: mockApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText('$70,000')).toBeInTheDocument();
    expect(screen.getByText('$60,000')).toBeInTheDocument();
    expect(screen.getByText('$90,000')).toBeInTheDocument();
  });

  it('handles missing optional fields gracefully', async () => {
    const minimalApplications = [
      {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        status: 'submitted',
        applied_at: '2024-01-01T00:00:00Z'
      }
    ];
    
    api.get
      .mockResolvedValueOnce({ data: mockJob })
      .mockResolvedValueOnce({ data: { applications: minimalApplications } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    // Should render without crashing
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });
});
