import api from './api';

export const recruiterService = {
  submitRequest: (reason) => 
    api.post('/recruiter-requests/', { reason }),
  
  getMyStatus: () => 
    api.get('/recruiter-requests/my-status'),
  
  getMyRequests: () => 
    api.get('/recruiter-requests/my-requests'),
};
