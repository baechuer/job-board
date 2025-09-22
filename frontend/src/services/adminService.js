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
};
