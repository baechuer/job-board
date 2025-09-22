import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Header = () => {
  const { user, logout, isAdmin, isRecruiter } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-primary-600">
              JobBoard
            </Link>
          </div>

          {/* Actions cluster (RHS) */}
          <div className="flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-3">
                {/* Welcome should be leftmost in the cluster */}
                <span className="text-gray-700 hidden md:inline">Welcome, {user.username}</span>
                {/* Admin action clustered with others */}
                {isAdmin() && (
                  <Link to="/admin/recruiter-requests" className="btn-secondary">
                    Admin
                  </Link>
                )}
                <Link to="/profile" className="btn-secondary">
                  Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="btn-secondary"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                {location.pathname !== '/login' && (
                  <Link to="/login" className="btn-secondary">
                    Login
                  </Link>
                )}
                {location.pathname !== '/register' && (
                  <Link to="/register" className="btn-primary">
                    Register
                  </Link>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
