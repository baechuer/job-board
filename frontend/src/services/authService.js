import api from './api';

export const authService = {
  login: (email, password) => 
    api.post('/auth/login', { email, password }),
  
  register: (userData) => 
    api.post('/auth/register', userData),
  
  refreshToken: () => 
    api.post('/auth/refresh'),
  
  getProfile: () => 
    api.get('/auth/me'),
  
  logout: () => 
    api.post('/auth/logout'),
  
  verifyEmail: (token) => 
    api.get(`/auth/verify-email?token=${token}`),
  
  requestPasswordReset: (email) => 
    api.post('/auth/request-password-reset', { email }),
  
  resetPassword: (token, password) => 
    api.post('/auth/reset-password', { token, password }),
};
