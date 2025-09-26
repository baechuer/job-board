import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const applicationService = {
  async applyForJob(jobId, formData) {
    const token = localStorage.getItem('token');
    
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
    };

    const response = await axios.post(
      `${API_BASE_URL}/applications/jobs/${jobId}/apply`,
      formData,
      config
    );
    
    return response.data;
  },

  async getMyApplications(page = 1, perPage = 20) {
    const token = localStorage.getItem('token');
    
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    };

    const response = await axios.get(
      `${API_BASE_URL}/applications/my-applications?page=${page}&per_page=${perPage}`,
      config
    );
    
    return response.data;
  },

  async getJobApplications(jobId, page = 1, perPage = 20) {
    const token = localStorage.getItem('token');
    
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    };

    const response = await axios.get(
      `${API_BASE_URL}/applications/jobs/${jobId}/applications?page=${page}&per_page=${perPage}`,
      config
    );
    
    return response.data;
  },

  async downloadResume(applicationId) {
    const token = localStorage.getItem('token');
    
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      responseType: 'blob',
    };

    const response = await axios.get(
      `${API_BASE_URL}/applications/applications/${applicationId}/resume`,
      config
    );
    
    return response.data;
  },

  async downloadCoverLetter(applicationId) {
    const token = localStorage.getItem('token');
    
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      responseType: 'blob',
    };

    const response = await axios.get(
      `${API_BASE_URL}/applications/applications/${applicationId}/cover-letter`,
      config
    );
    
    return response.data;
  },
};

export default applicationService;
