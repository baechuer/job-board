import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MyJobs from './MyJobs';
import api from '../../services/api';

vi.mock('../../services/api', () => ({ default: { get: vi.fn() } }));

const renderPage = () => {
  const qc = new QueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <MyJobs />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

it('renders jobs table', async () => {
  api.get.mockResolvedValue({ data: { jobs: [
    { id: 1, title: 'A', location: 'Remote', employment_type: 'full_time', salary_min: 1, salary_max: 2, application_deadline: '2025-10-31', created_at: '2025-01-01', status: 'active' },
  ], pages: 1 } });
  renderPage();
  await waitFor(() => screen.getByText(/My Jobs/i));
  expect(screen.getByText('A')).toBeInTheDocument();
  expect(screen.getByText('Remote')).toBeInTheDocument();
});

it('shows error', async () => {
  api.get.mockRejectedValueOnce({ response: { data: { error: 'boom' } } });
  renderPage();
  await waitFor(() => screen.getByText(/boom/i));
});

it('toggles archived and shows empty message', async () => {
  // First call (active page 1)
  api.get.mockResolvedValueOnce({ data: { jobs: [
    { id: 1, title: 'A', location: 'Remote', employment_type: 'full_time', salary_min: 1, salary_max: 2, application_deadline: '2030-10-31', created_at: '2025-01-01', status: 'active' },
  ], pages: 1 } });
  // Prefetch archived page 1
  api.get.mockResolvedValueOnce({ data: { jobs: [], pages: 1 } });
  renderPage();
  await waitFor(() => screen.getByText('A'));
  fireEvent.click(screen.getByRole('button', { name: /show archived/i }));
  await waitFor(() => screen.getByText(/No archived jobs/i));
});


