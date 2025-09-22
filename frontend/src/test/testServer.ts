import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

const API = 'http://localhost:5000/api';

export const server = setupServer(
  // Auth endpoints
  http.post(`${API}/auth/login`, async () => {
    return HttpResponse.json({ access_token: 'fake-token' });
  }),
  http.post(`${API}/auth/refresh`, async () => {
    return HttpResponse.json({ access_token: 'new-fake-token' });
  }),
  http.get(`${API}/auth/me`, async () => {
    return HttpResponse.json({ user: { id: 1, email: 'me@me.com', username: 'me', roles: [{ role: 'candidate' }] } });
  }),

  // Recruiter request endpoints
  http.post(`${API}/recruiter-requests/`, async () => {
    return HttpResponse.json({ id: 1, status: 'pending' }, { status: 201 });
  }),
  http.get(`${API}/recruiter-requests/my-status`, async () => {
    return HttpResponse.json({ status: 'pending', message: 'Your request is under review' });
  }),

  // Admin recruiter requests
  http.get(`${API}/admin/recruiter-requests`, async () => {
    return HttpResponse.json({
      requests: [
        { id: 1, status: 'pending', reason: 'I want to recruit', submitted_at: new Date().toISOString(), user: { username: 'john', email: 'john@example.com' } },
      ],
      total: 1,
      pages: 1,
      current_page: 1,
      per_page: 10,
    });
  }),
  http.put(`${API}/admin/recruiter-requests/:id/approve`, async () => {
    return HttpResponse.json({ message: 'Request approved successfully' });
  }),
  http.put(`${API}/admin/recruiter-requests/:id/reject`, async () => {
    return HttpResponse.json({ message: 'Request rejected successfully' });
  })
);
