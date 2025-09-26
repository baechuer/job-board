import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import UserDetail from './UserDetail';

vi.mock('../../services/adminService', () => ({
  adminService: {
    getUserById: vi.fn(() => Promise.resolve({ data: { id: 1, email: 'u@example.com', username: 'u', roles: ['candidate'] } })),
    updateUserById: vi.fn(() => Promise.resolve({ data: { msg: 'user updated' } })),
  }
}));

describe('Admin UserDetail', () => {
  it('loads user and saves updates', async () => {
    render(
      <MemoryRouter initialEntries={["/admin/users/1"]}>
        <Routes>
          <Route path="/admin/users/:id" element={<UserDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for load
    await waitFor(() => expect(screen.getByDisplayValue('u')).toBeInTheDocument());

    // Change username and role, then save
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'u2' } });
    fireEvent.change(screen.getByLabelText(/role/i), { target: { value: 'recruiter' } });
    fireEvent.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() => expect(screen.getByText(/user updated/i)).toBeInTheDocument());
  });
});


