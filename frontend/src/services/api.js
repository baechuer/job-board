import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Do not attempt refresh on auth endpoints themselves
    const url = (originalRequest?.url || '').toString();
    const isAuthEndpoint = (
      url.includes('/auth/login') ||
      url.includes('/auth/register') ||
      url.includes('/auth/verify') ||
      url.includes('/auth/password/reset') ||
      url.includes('/auth/password/reset/verify')
    );

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isAuthEndpoint) {
        return Promise.reject(error);
      }
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        const refreshResponse = await axios.post(
          `${API_BASE_URL}/auth/refresh`,
          null,
          { headers: { Authorization: `Bearer ${refreshToken}` } }
        );
        const { access_token } = refreshResponse.data || {};
        
        localStorage.setItem('token', access_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        
        return api(originalRequest);
      } catch (refreshError) {
        // Clear bad tokens; let UI handle state gracefully
        try {
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
        } catch {}
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
