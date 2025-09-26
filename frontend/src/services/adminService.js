import api from './api';

export const adminService = {
  getRecruiterRequests: (params) => 
    api.get('/admin/recruiter-requests', { params }),
  
  approveRequest: (id, notes) => 
    api.put(`/admin/recruiter-requests/${id}/approve`, { notes }),
  
  rejectRequest: (id, notes) => 
    api.put(`/admin/recruiter-requests/${id}/reject`, { notes }),
  
  markRequestsAsViewed: () => 
    api.post('/admin/recruiter-requests/mark-viewed'),
  
  cleanupCompletedRequests: () => 
    api.post('/admin/recruiter-requests/cleanup'),

  getMetrics: () => 
    api.get('/admin/metrics', { validateStatus: (s) => s === 200 || s === 304 }),

  getRecentActivity: () =>
    api.get('/admin/activity_recent'),

  listUsers: (params, options = {}) => 
    api.get('/admin/users', { params, ...options }),

  requestProfileCode: () =>
    api.post('/auth/profile/update/request-code'),

  verifyProfileCode: (code) =>
    api.post('/auth/profile/update/verify-code', { code }),

  updateProfile: (payload) =>
    api.put('/auth/profile', payload),

  getUserById: (id) =>
    api.get(`/admin/users/${id}`),

  updateUserById: (id, payload) =>
    api.put(`/admin/users/${id}`, payload),
};
