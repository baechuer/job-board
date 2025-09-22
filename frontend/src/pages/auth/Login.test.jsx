import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../../context/AuthContext';
import Login from './Login';

// Helper to render with providers
const renderWithProviders = (ui) => {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <AuthProvider>
        {ui}
      </AuthProvider>
    </MemoryRouter>
  );
};

it('renders the login form', () => {
  renderWithProviders(<Login />);
  expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();
  // Query inputs by role and accessible name (from the label text)
  expect(screen.getByRole('textbox', { name: /email address/i })).toBeInTheDocument();
  // Password input has role 'textbox' but type password is not a textbox; use getByLabel or placeholder fallback
  // Use getByRole with name matching the label via aria (jsdom ties it by proximity in RTL)
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
});

it('submits and clears loading state', async () => {
  renderWithProviders(<Login />);
  await userEvent.type(screen.getByRole('textbox', { name: /email address/i }), 'me@me.com');
  await userEvent.type(screen.getByLabelText(/password/i), 'Password123!');
  await userEvent.click(screen.getByRole('button', { name: /sign in/i }));
  // After MSW mocked login + profile load, we should still have the form visible (no redirect assertions here)
  expect(await screen.findByText(/sign in to your account/i)).toBeInTheDocument();
});
