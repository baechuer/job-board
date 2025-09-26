import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Jobs from './Jobs';

const renderPage = (fetcher) => {
  const qc = new QueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Jobs fetcher={fetcher} />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

async function wait(ms) {
  await new Promise((r) => setTimeout(r, ms));
}

it('calls fetcher on mount', async () => {
  const fake = vi.fn(() => Promise.resolve({ jobs:[{ id:1, title:'React Dev', location:'Remote', skills:['react'] }], pages:1, current_page:1 }));
  renderPage(fake);
  await waitFor(() => expect(fake).toHaveBeenCalledTimes(1));
});

it('debounces search input and cancels previous requests', async () => {
  const fake = vi.fn(() => Promise.resolve({ jobs: [], pages:1, current_page:1 }));
  renderPage(fake);
  await waitFor(() => expect(fake).toHaveBeenCalledTimes(1));

  const input = screen.getByPlaceholderText(/Search by job title or skills/i);

  fake.mockResolvedValue({ jobs: [ { id:1, title:'React Dev', location:'Remote', skills:['react'] } ], pages:1, current_page:1 });
  fireEvent.change(input, { target: { value: 'r' } });
  fireEvent.change(input, { target: { value: 're' } });
  fireEvent.change(input, { target: { value: 'rea' } });

  await wait(200);
  expect(fake).toHaveBeenCalledTimes(1);

  await wait(150);
  await waitFor(() => expect(fake).toHaveBeenCalledTimes(2));

  const clearBtn = await screen.findByRole('button', { name: /clear/i });
  fake.mockResolvedValueOnce({ jobs: [], pages:1, current_page:1 });
  fireEvent.click(clearBtn);
  await waitFor(() => expect(fake).toHaveBeenCalledTimes(3));
});


