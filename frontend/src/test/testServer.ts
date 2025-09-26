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
  }),

  // Recruiter job management
  http.get(`${API}/recruiter/my-jobs/:id`, async () => {
    return HttpResponse.json({
      id: 1,
      title: 'Software Engineer',
      description: 'A great job opportunity',
      location: 'San Francisco',
      salary_min: 50000,
      salary_max: 80000,
      employment_type: 'full_time',
      seniority: 'mid',
      work_mode: 'remote',
      status: 'active',
      created_at: '2024-01-01T00:00:00Z'
    });
  }),

  // Application management
  http.get(`${API}/applications/jobs/:jobId/applications`, async () => {
    return HttpResponse.json({
      applications: [
        {
          id: 1,
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '123-456-7890',
          current_company: 'Tech Corp',
          experience: '3-5 years',
          salary_expectation: 70000,
          status: 'submitted',
          applied_at: '2024-01-01T00:00:00Z',
          additional_info: 'Passionate developer'
        },
        {
          id: 2,
          first_name: 'Jane',
          last_name: 'Smith',
          email: 'jane@example.com',
          phone: '987-654-3210',
          current_company: 'Startup Inc',
          experience: '1-2 years',
          salary_expectation: 60000,
          status: 'accepted',
          applied_at: '2024-01-02T00:00:00Z',
          additional_info: 'Eager to learn'
        }
      ],
      pagination: {
        total: 2,
        pages: 1,
        current_page: 1,
        per_page: 20
      }
    });
  }),

  http.get(`${API}/applications/:applicationId`, async () => {
    return HttpResponse.json({
      id: 1,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      phone: '123-456-7890',
      current_company: 'Tech Corp',
      current_position: 'Developer',
      experience: '3-5 years',
      education: 'bachelor',
      skills: 'Python, JavaScript, React',
      portfolio: 'https://johndoe.com',
      linkedin: 'https://linkedin.com/in/johndoe',
      github: 'https://github.com/johndoe',
      availability: 'Immediately',
      salary_expectation: 70000,
      notice_period: '2 weeks',
      work_authorization: 'US Citizen',
      relocation: 'Yes',
      additional_info: 'Passionate about technology',
      status: 'submitted',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      resume_path: 'resumes/john_doe_resume.pdf',
      cover_letter_path: 'cover_letters/john_doe_cover_letter.pdf',
      job: {
        id: 1,
        title: 'Software Engineer',
        location: 'San Francisco',
        employment_type: 'full_time',
        seniority: 'mid',
        work_mode: 'remote',
        salary_min: 50000,
        salary_max: 80000
      }
    });
  }),

  http.patch(`${API}/applications/:applicationId/status`, async () => {
    return HttpResponse.json({
      message: 'Application status updated successfully',
      application_id: 1,
      status: 'accepted'
    });
  }),

  http.get(`${API}/applications/:applicationId/resume`, async () => {
    return new HttpResponse('fake pdf content', {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="john_doe_resume.pdf"'
      }
    });
  }),

  http.get(`${API}/applications/:applicationId/cover-letter`, async () => {
    return new HttpResponse('fake cover letter content', {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="john_doe_cover_letter.pdf"'
      }
    });
  })
);
