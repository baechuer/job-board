import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Sidebar = () => {
  const { user, isAdmin, isRecruiter, isCandidate } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const getDashboardPath = () => {
    if (isAdmin()) return '/dashboard/admin';
    if (isRecruiter()) return '/dashboard/recruiter';
    if (isCandidate()) return '/dashboard/candidate';
    return '/dashboard';
  };

  return (
    <aside className="w-64 bg-white shadow-sm border-r border-gray-200 min-h-screen">
      <div className="p-6">
        <nav className="space-y-2">
          <Link
            to={getDashboardPath()}
            className={`block px-3 py-2 rounded-lg ${
              isActive(getDashboardPath()) 
                ? 'bg-primary-100 text-primary-700' 
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            Dashboard
          </Link>

          {isAdmin() && (
            <Link
              to="/admin/recruiter-requests"
              className={`block px-3 py-2 rounded-lg ${
                isActive('/admin/recruiter-requests') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Recruiter Requests
            </Link>
          )}

          <Link
            to="/profile"
            className={`block px-3 py-2 rounded-lg ${
              isActive('/profile') 
                ? 'bg-primary-100 text-primary-700' 
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            Profile
          </Link>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
