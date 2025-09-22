import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { user, isAdmin, isRecruiter, isCandidate } = useAuth();

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Find Your Dream Job
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Connect with top companies and talented professionals
        </p>
        
        {!user ? (
          <div className="space-x-4">
            <Link to="/register" className="btn-primary text-lg px-8 py-3">
              Get Started
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-3">
              Sign In
            </Link>
          </div>
        ) : (
          <div className="space-x-4">
            <Link to={`/dashboard/${user.roles?.[0]?.role || 'candidate'}`} className="btn-primary text-lg px-8 py-3">
              Go to Dashboard
            </Link>
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-3 gap-8 py-12">
        <div className="card text-center">
          <div className="text-4xl mb-4">🔐</div>
          <h3 className="text-xl font-semibold mb-2">Secure Platform</h3>
          <p className="text-gray-600">
            Secure authentication and role-based access control
          </p>
        </div>
        
        <div className="card text-center">
          <div className="text-4xl mb-4">👥</div>
          <h3 className="text-xl font-semibold mb-2">Role Management</h3>
          <p className="text-gray-600">
            Admin, Recruiter, and Candidate roles with appropriate permissions
          </p>
        </div>
        
        <div className="card text-center">
          <div className="text-4xl mb-4">📋</div>
          <h3 className="text-xl font-semibold mb-2">Request System</h3>
          <p className="text-gray-600">
            Submit and manage recruiter access requests
          </p>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-primary-50 rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold text-primary-800 mb-4">
          Join Thousands of Professionals
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <div className="text-3xl font-bold text-primary-600">8</div>
            <div className="text-primary-700">Registered Users</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-600">2</div>
            <div className="text-primary-700">Active Recruiters</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-600">1</div>
            <div className="text-primary-700">Admin Users</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
