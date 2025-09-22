import { useAuth } from '../../context/AuthContext';

const AdminDashboard = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600">Welcome back, {user?.username}</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="text-2xl font-bold text-primary-600">12</div>
          <div className="text-gray-600">Pending Requests</div>
        </div>
        
        <div className="card">
          <div className="text-2xl font-bold text-green-600">156</div>
          <div className="text-gray-600">Total Users</div>
        </div>
        
        <div className="card">
          <div className="text-2xl font-bold text-blue-600">89</div>
          <div className="text-gray-600">Active Jobs</div>
        </div>
        
        <div className="card">
          <div className="text-2xl font-bold text-purple-600">45</div>
          <div className="text-gray-600">Recruiters</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="btn-primary w-full">
              Review Recruiter Requests
            </button>
            <button className="btn-secondary w-full">
              Manage Users
            </button>
            <button className="btn-secondary w-full">
              System Settings
            </button>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">New recruiter request from john.doe@example.com</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm">User jane.smith registered</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm">Job posting "Senior Developer" was created</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
