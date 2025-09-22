import { render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import RecruiterRequests from './RecruiterRequests';
import { AuthProvider } from '../../context/AuthContext';

const renderWithProviders = (ui) => render(
  <MemoryRouter>
    <AuthProvider>
      {ui}
    </AuthProvider>
  </MemoryRouter>
);

it('renders recruiter requests list', async () => {
  renderWithProviders(<RecruiterRequests />);
  // Heading
  expect(await screen.findByRole('heading', { level: 1, name: /recruiter requests/i })).toBeInTheDocument();
  // Table header
  expect(await screen.findByRole('columnheader', { name: /user/i })).toBeInTheDocument();
  expect(screen.getByRole('columnheader', { name: /status/i })).toBeInTheDocument();
  // Row content
  const row = await screen.findByRole('row', { name: /john/i });
  expect(within(row).getByText(/pending/i)).toBeInTheDocument();
});
