import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { adminService } from '../../services/adminService';

const AdminDashboard = () => {
  const { user, token, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      if (!isAdmin()) {
        setLoading(false);
        return;
      }
      try {
        const res = await adminService.getMetrics();
        // Support 304: if cached by axios interceptor, res may be last data
        if (res.status === 200 && mounted) {
          setMetrics(res.data);
        }
        const a = await adminService.getRecentActivity();
        if (a.status === 200 && mounted) setActivity(a.data?.items || []);
      } catch (e) {
        if (mounted) setError(e);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    const id = setInterval(load, 60000);
    return () => { mounted = false; clearInterval(id); };
  }, [token]);

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600">Welcome back, {user?.username}</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {loading ? (
          <>
            <div className="card animate-pulse h-20" />
            <div className="card animate-pulse h-20" />
            <div className="card animate-pulse h-20" />
            <div className="card animate-pulse h-20" />
          </>
        ) : error ? (
          <div className="col-span-4 card text-red-600">Failed to load metrics</div>
        ) : (
          <>
            <div className="card">
              <div className="text-2xl font-bold text-primary-600">{metrics?.pending_recruiter_requests ?? 0}</div>
              <div className="text-gray-600">Pending Requests</div>
            </div>
            <div className="card">
              <div className="text-2xl font-bold text-green-600">{metrics?.total_users ?? 0}</div>
              <div className="text-gray-600">Total Users</div>
            </div>
            <div className="card">
              <div className="text-2xl font-bold text-blue-600">{metrics?.active_jobs ?? 0}</div>
              <div className="text-gray-600">Active Jobs</div>
            </div>
            <div className="card">
              <div className="text-2xl font-bold text-purple-600">{metrics?.total_recruiters ?? 0}</div>
              <div className="text-gray-600">Recruiters</div>
            </div>
          </>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="btn-primary w-full" onClick={() => navigate('/admin/recruiter-requests')}>
              Review Recruiter Requests
            </button>
            <button className="btn-secondary w-full" onClick={() => navigate('/admin/users')}>
              Manage Users
            </button>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {activity.length === 0 ? (
              <div className="text-sm text-gray-500">No recent activity</div>
            ) : (
              activity.map((it, idx) => (
                <div key={idx} className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${it.level === 'success' ? 'bg-green-500' : it.level === 'warning' ? 'bg-yellow-500' : it.level === 'primary' ? 'bg-blue-500' : 'bg-gray-400'}`}></div>
                  <span className="text-sm">{it.message}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
