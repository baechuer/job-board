import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await authService.getProfile();
          setUser(userData?.data?.user || userData.user);
        } catch (error) {
          console.error('Auth initialization failed:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await authService.login(email, password);
      const { access_token, refresh_token } = response?.data || {};
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      if (refresh_token) {
        try { localStorage.setItem('refresh_token', refresh_token); } catch {}
      }
      
      const userData = await authService.getProfile();
      setUser(userData?.data?.user || userData.user);
      
      // Clear pending verification email on successful login
      try { localStorage.removeItem('pendingVerificationEmail'); } catch {}
      
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      // Prefer Marshmallow validation messages when present (422)
      const messages = error?.response?.data?.messages || error?.response?.data?.details;
      let msg = error?.response?.data?.error || error?.response?.data?.message || error.message || 'Login failed';
      if (messages) {
        try {
          // Flatten messages object into a readable string
          const parts = [];
          Object.entries(messages).forEach(([field, errs]) => {
            const arr = Array.isArray(errs) ? errs : [errs];
            arr.forEach(e => parts.push(`${field}: ${e}`));
          });
          if (parts.length) msg = parts.join('\n');
        } catch {}
      }
      return { success: false, error: msg };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authService.register(userData);
      return { success: true, data: response?.data ?? response };
    } catch (error) {
      console.error('Registration failed:', error);
      const msg = error?.response?.data?.error || error?.response?.data?.message || error.message || 'Registration failed';
      return { success: false, error: msg, details: error?.response?.data?.details };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const refreshToken = async () => {
    try {
      const response = await authService.refreshToken();
      const { access_token } = response?.data || {};
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      return { success: true };
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      return { success: false };
    }
  };

  const hasRole = (role) => {
    return user?.roles?.some(userRole => userRole.role === role);
  };

  const isAdmin = () => hasRole('admin');
  const isRecruiter = () => hasRole('recruiter');
  const isCandidate = () => hasRole('candidate');

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    refreshToken,
    hasRole,
    isAdmin,
    isRecruiter,
    isCandidate,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
