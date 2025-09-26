import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const RoleRoute = ({ role, children }) => {
  const { loading, user, hasRole } = useAuth();
  if (loading) return null;
  if (!user || (role && !hasRole(role))) return <Navigate to="/" replace />;
  return children;
};

export default RoleRoute;


