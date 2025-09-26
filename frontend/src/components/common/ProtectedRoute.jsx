import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { user, token, loading } = useAuth();
  const location = useLocation();

  if (loading) return null;
  if (!token || !user) return <Navigate to="/login" replace state={{ from: location }} />;

  return children;
};

export default ProtectedRoute;


