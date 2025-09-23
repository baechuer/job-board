import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import JobDetail from './JobDetail';
import api from '../../services/api';

vi.mock('../../services/api', () => ({ default: { get: vi.fn() } }));

const renderPage = (id = '1') => render(
  <MemoryRouter initialEntries={[`/recruiter/my-jobs/${id}`]}>
    <Routes>
      <Route path="/recruiter/my-jobs/:id" element={<JobDetail />} />
    </Routes>
  </MemoryRouter>
);

it('renders job detail', async () => {
  api.get.mockResolvedValue({ data: {
    id: 1, title: 'Detail', description: 'desc', location: 'Remote', employment_type: 'full_time', seniority: 'mid', work_mode: 'remote',
    salary_min: 1, salary_max: 2, requirements: ['req'], skills: ['skill'], responsibilities: 'resp', created_at: '2025-01-01T00:00:00Z', status: 'active'
  } });
  renderPage('1');
  await waitFor(() => screen.getByText(/Detail/i));
  expect(screen.getByText(/Full Time/i)).toBeInTheDocument();
  expect(screen.getAllByText(/Remote/i).length).toBeGreaterThanOrEqual(1);
});


