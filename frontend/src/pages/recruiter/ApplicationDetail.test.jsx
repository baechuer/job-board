import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';
import ApplicationDetail from './ApplicationDetail';
import api from '../../services/api';

vi.mock('../../services/api', () => ({ default: { get: vi.fn(), patch: vi.fn() } }));

const mockApplication = {
  id: 1,
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com',
  phone: '123-456-7890',
  current_company: 'Tech Corp',
  current_position: 'Software Engineer',
  experience: '3-5 years',
  education: 'Bachelor of Computer Science',
  skills: 'React, Node.js, Python',
  portfolio: 'https://johndoe.dev',
  linkedin: 'https://linkedin.com/in/johndoe',
  github: 'https://github.com/johndoe',
  availability: 'Immediate',
  salary_expectation: '70000',
  notice_period: '2 weeks',
  work_authorization: 'Yes',
  relocation: 'No',
  additional_info: 'Passionate developer',
  status: 'submitted',
  created_at: '2024-01-01T11:00:00Z',
  updated_at: '2024-01-01T11:00:00Z',
  resume_path: 'applications/1/resume.pdf',
  cover_letter_path: 'applications/1/cover.pdf',
  job: {
    id: 1,
    title: 'Software Engineer',
    location: 'San Francisco',
    employment_type: 'Full-time',
    seniority: 'Mid-level',
    work_mode: 'Hybrid',
    salary_min: 80000,
    salary_max: 120000,
  }
};

const renderPage = (applicationId = '1') => render(
  <MemoryRouter initialEntries={[`/recruiter/applications/${applicationId}`]}>
    <Routes>
      <Route path="/recruiter/applications/:applicationId" element={<ApplicationDetail />} />
    </Routes>
  </MemoryRouter>
);

describe('ApplicationDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders application details correctly', async () => {
    api.get.mockResolvedValue({ data: mockApplication });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText('← Back to Applications')).toBeInTheDocument();
    expect(screen.getAllByText('Software Engineer')).toHaveLength(3);
    expect(screen.getAllByText('San Francisco')).toHaveLength(2);
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
    expect(screen.getByText('123-456-7890')).toBeInTheDocument();
    expect(screen.getByText('Tech Corp')).toBeInTheDocument();
    expect(screen.getByText('3-5 years')).toBeInTheDocument();
    expect(screen.getByText('Bachelor of Computer Science')).toBeInTheDocument();
    expect(screen.getByText('Passionate developer')).toBeInTheDocument();
  });

  it('renders links section when links are provided', async () => {
    api.get.mockResolvedValue({ data: mockApplication });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText('Portfolio:')).toBeInTheDocument();
    expect(screen.getByText('LinkedIn:')).toBeInTheDocument();
    expect(screen.getByText('GitHub:')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'https://johndoe.dev' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'https://linkedin.com/in/johndoe' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'https://github.com/johndoe' })).toBeInTheDocument();
  });

  it('renders status action buttons for submitted status', async () => {
    api.get.mockResolvedValue({ data: mockApplication });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText('Mark as Reviewing')).toBeInTheDocument();
    expect(screen.getByText('Accept')).toBeInTheDocument();
    expect(screen.getByText('Reject')).toBeInTheDocument();
  });

  it('renders status action buttons for reviewed status', async () => {
    const reviewedApplication = { ...mockApplication, status: 'reviewed' };
    api.get.mockResolvedValue({ data: reviewedApplication });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText('Accept')).toBeInTheDocument();
    expect(screen.getByText('Reject')).toBeInTheDocument();
    expect(screen.queryByText('Mark as Reviewing')).not.toBeInTheDocument();
  });

  it('renders document section with view and download buttons', async () => {
    api.get.mockResolvedValue({ data: mockApplication });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText('Documents')).toBeInTheDocument();
    expect(screen.getByText('Resume')).toBeInTheDocument();
    expect(screen.getByText('Cover Letter')).toBeInTheDocument();
    expect(screen.getAllByText('View Online')).toHaveLength(2);
    expect(screen.getAllByText('Download')).toHaveLength(2);
  });

  it('renders job information sidebar', async () => {
    api.get.mockResolvedValue({ data: mockApplication });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText('Job Information')).toBeInTheDocument();
    expect(screen.getByText('Location:')).toBeInTheDocument();
    expect(screen.getByText('Full-time')).toBeInTheDocument();
    expect(screen.getByText('Mid-level')).toBeInTheDocument();
    expect(screen.getByText('Hybrid')).toBeInTheDocument();
    expect(screen.getByText('Salary Range:')).toBeInTheDocument();
  });

  it('handles status update successfully', async () => {
    api.get.mockResolvedValue({ data: mockApplication });
    api.patch.mockResolvedValue({ data: { message: 'Status updated successfully' } });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    const acceptButton = screen.getByText('Accept');
    fireEvent.click(acceptButton);
    
    await waitFor(() => {
      expect(api.patch).toHaveBeenCalledWith('/applications/1/status', {
        status: 'accepted'
      });
    });
  });

  it('shows loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderPage('1');
    
    expect(screen.getAllByRole('generic')).toHaveLength(9); // Loading skeleton elements
  });

  it('shows error state when API call fails', async () => {
    api.get.mockRejectedValue(new Error('API Error'));
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('Failed to load application details'));
  });

  it('shows not found state when application is null', async () => {
    api.get.mockResolvedValue({ data: null });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('Application Not Found'));
  });

  it('handles missing optional fields gracefully', async () => {
    const minimalApplication = {
      ...mockApplication,
      portfolio: null,
      linkedin: null,
      github: null,
      additional_info: null
    };
    api.get.mockResolvedValue({ data: minimalApplication });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.queryByText('Portfolio:')).not.toBeInTheDocument();
    expect(screen.queryByText('LinkedIn:')).not.toBeInTheDocument();
    expect(screen.queryByText('GitHub:')).not.toBeInTheDocument();
  });

  it('formats dates correctly', async () => {
    api.get.mockResolvedValue({ data: mockApplication });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText(/Applied Date:/)).toBeInTheDocument();
    expect(screen.getByText(/Last Updated:/)).toBeInTheDocument();
  });

  it('formats salary correctly', async () => {
    api.get.mockResolvedValue({ data: mockApplication });
    
    renderPage('1');
    
    await waitFor(() => screen.getByText('John Doe'));
    
    expect(screen.getByText('Salary Expectation:')).toBeInTheDocument();
    expect(screen.getByText('$80,000 - $120,000')).toBeInTheDocument();
  });
});
