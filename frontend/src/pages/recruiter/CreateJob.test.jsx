import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CreateJob from './CreateJob';
import api from '../../services/api';

vi.mock('../../services/api', () => ({ default: { post: vi.fn() } }));

const renderPage = () => render(
  <BrowserRouter>
    <CreateJob />
  </BrowserRouter>
);

it('submits extended payload and handles success', async () => {
  api.post.mockResolvedValue({ status: 201, data: { status: 'created' } });
  renderPage();

  fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Backend Dev' } });
  fireEvent.change(screen.getByLabelText(/^Description$/i), { target: { value: 'Build APIs' } });
  fireEvent.change(screen.getByLabelText(/Salary Min/i), { target: { value: '100000' } });
  fireEvent.change(screen.getByLabelText(/Salary Max/i), { target: { value: '150000' } });
  fireEvent.change(screen.getByLabelText(/^Location$/i), { target: { value: 'Remote' } });
  fireEvent.change(screen.getByLabelText(/Requirements/), { target: { value: 'Python, Flask' } });
  fireEvent.change(screen.getByLabelText(/^Responsibilities$/i), { target: { value: 'Build stuff' } });
  fireEvent.change(screen.getByLabelText(/Skills/), { target: { value: 'SQL, Docker' } });
  fireEvent.change(screen.getByLabelText(/Application Deadline/i), { target: { value: '2025-10-31' } });

  // Extended fields
  fireEvent.change(screen.getByLabelText(/Employment Type/i, { selector: 'select' }), { target: { value: 'full_time' } });
  fireEvent.change(screen.getByLabelText(/Seniority/i, { selector: 'select' }), { target: { value: 'senior' } });
  fireEvent.change(screen.getByLabelText(/Work Mode/i, { selector: 'select' }), { target: { value: 'remote' } });
  fireEvent.change(screen.getByLabelText(/Visa Sponsorship/i, { selector: 'select' }), { target: { value: 'yes' } });
  fireEvent.change(screen.getByLabelText(/Work Authorization/i), { target: { value: 'US Citizen' } });
  fireEvent.change(screen.getByLabelText(/Nice to haves/i), { target: { value: 'GraphQL' } });
  fireEvent.change(screen.getByLabelText(/About team/i), { target: { value: 'Platform team' } });

  fireEvent.click(screen.getByRole('button', { name: /Post Job/i }));

  await waitFor(() => expect(api.post).toHaveBeenCalled());
  const body = api.post.mock.calls[0][1];
  expect(body.employment_type).toBe('full_time');
  expect(body.seniority).toBe('senior');
  expect(body.work_mode).toBe('remote');
  expect(body.visa_sponsorship).toBe(true);
  expect(body.requirements).toEqual(['Python', 'Flask']);
  expect(body.skills).toEqual(['SQL', 'Docker']);
});

it('shows backend error', async () => {
  api.post.mockRejectedValue({ response: { data: { error: 'conflict' } } });
  renderPage();

  // Fill minimal required fields so native validation doesn't block submit
  fireEvent.change(screen.getByLabelText(/^Title$/i), { target: { value: 'T' } });
  fireEvent.change(screen.getByLabelText(/^Description$/i), { target: { value: 'D'.repeat(10) } });
  fireEvent.change(screen.getByLabelText(/Salary Min/i), { target: { value: '1' } });
  fireEvent.change(screen.getByLabelText(/Salary Max/i), { target: { value: '2' } });
  fireEvent.change(screen.getByLabelText(/^Location$/i), { target: { value: 'L' } });
  fireEvent.change(screen.getByLabelText(/Requirements/), { target: { value: 'R' } });
  fireEvent.change(screen.getByLabelText(/^Responsibilities$/i), { target: { value: 'Res' } });
  fireEvent.change(screen.getByLabelText(/Skills/), { target: { value: 'S' } });
  fireEvent.change(screen.getByLabelText(/Application Deadline/i), { target: { value: '2025-10-31' } });

  fireEvent.click(screen.getByRole('button', { name: /Post Job/i }));
  await waitFor(() => screen.getByText(/conflict/i));
});


