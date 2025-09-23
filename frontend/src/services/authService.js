import api, { API_BASE_URL } from './api';
import axios from 'axios';

export const authService = {
  login: (email, password) => 
    api.post('/auth/login', { email, password }),
  
  register: (userData) => 
    api.post('/auth/register', userData),
  
  refreshToken: () => 
    api.post('/auth/refresh'),
  
  getProfile: () => 
    api.get('/auth/me'),
  
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (_) {}

    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await axios.post(`${API_BASE_URL}/auth/logout_refresh`, null, {
          headers: { Authorization: `Bearer ${refreshToken}` },
          // Avoid api instance to prevent access-token header interception
          validateStatus: () => true,
        });
      }
    } catch (_) {}

    try {
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
    } catch (_) {}
  },
  
  verifyEmail: (token) => 
    api.get(`/auth/verify?token=${encodeURIComponent(token)}`),
  
  requestPasswordReset: (email) => 
    api.post('/auth/password/reset', { email }),
  
  resetPassword: (token, new_password) => 
    api.post('/auth/password/reset/verify', { token, new_password }),
};
