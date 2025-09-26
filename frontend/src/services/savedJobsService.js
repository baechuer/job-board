import api from './api';

export const savedJobsService = {
  getStatus: (jobId) => api.get(`/candidate/saved-jobs/status/${jobId}`),
  save: (jobId) => api.post(`/candidate/saved-jobs/${jobId}`),
  unsave: (jobId) => api.delete(`/candidate/saved-jobs/${jobId}`),
  list: (page = 1, per_page = 20) => api.get('/candidate/saved-jobs', { params: { page, per_page } }),
};


