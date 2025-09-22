import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RecruiterRequestForm from './RecruiterRequestForm';

it('submits recruiter request and calls onSuccess', async () => {
  const onSuccess = vi.fn();
  render(<RecruiterRequestForm onSuccess={onSuccess} />);

  await userEvent.type(screen.getByRole('textbox', { name: /why do you/i }), 'I hire engineers');
  await userEvent.click(screen.getByRole('button', { name: /submit request/i }));

  expect(onSuccess).toHaveBeenCalled();
});
