import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';

const RecruiterDashboard = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Recruiter Dashboard</h1>
        <p className="text-gray-600">Welcome back, {user?.username}</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="text-2xl font-bold text-primary-600">0</div>
          <div className="text-gray-600">Active Jobs</div>
        </div>
        
        <div className="card">
          <div className="text-2xl font-bold text-green-600">0</div>
          <div className="text-gray-600">Applications</div>
        </div>
        
        <div className="card">
          <div className="text-2xl font-bold text-blue-600">0</div>
          <div className="text-gray-600">Interviews</div>
        </div>
        
        <div className="card">
          <div className="text-2xl font-bold text-purple-600">0</div>
          <div className="text-gray-600">Hires</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Link to="/recruiter/create-job" className="btn-primary inline-block">Post Job</Link>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Recruiter Status</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">Recruiter role active</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm">Ready to post jobs (coming soon)</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm">Job management features in development</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecruiterDashboard;
