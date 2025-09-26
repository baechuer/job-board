import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Profile from './Profile';
import { MemoryRouter } from 'react-router-dom';
import * as AuthContext from '../../context/AuthContext';

vi.mock('../../services/adminService', () => ({
  adminService: {
    requestProfileCode: vi.fn(() => Promise.resolve({ data: { msg: 'ok' } })),
    verifyProfileCode: vi.fn(() => Promise.resolve({ data: { msg: 'ok' } })),
    updateProfile: vi.fn(() => Promise.resolve({ data: { msg: 'ok' } })),
  }
}));

function Wrapper({ children }) {
  return <MemoryRouter>{children}</MemoryRouter>;
}

describe('Profile edit with code flow', () => {
  beforeEach(() => {
    try { localStorage.removeItem('token'); } catch {}
    vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
      user: { id: 1, email: 'user@example.com', username: 'user', roles: [{ role: 'candidate' }] },
    });
  });

  it('allows requesting code, verifying, and saving', async () => {
    render(<Wrapper><Profile /></Wrapper>);

    // Enter edit mode
    fireEvent.click(screen.getByRole('button', { name: /edit profile/i }));

    // Send code
    fireEvent.click(screen.getByRole('button', { name: /send verification code/i }));
    await waitFor(() => expect(screen.getByText(/verification code sent/i)).toBeInTheDocument());

    // Enter code and verify
    const input = screen.getByLabelText(/6-digit code/i);
    fireEvent.change(input, { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: /verify code/i }));
    await waitFor(() => expect(screen.getByText(/code verified/i)).toBeInTheDocument());

    // Save changes
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));
    await waitFor(() => expect(screen.getByText(/profile updated/i)).toBeInTheDocument());
  });
});


