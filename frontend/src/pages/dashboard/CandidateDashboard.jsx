import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { savedJobsService } from '../../services/savedJobsService';
import applicationService from '../../services/applicationService';

const CandidateDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    applications: 0,
    interviews: 0,
    savedJobs: 0,
    jobAlerts: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      
      // Load applications count
      const applicationsResponse = await applicationService.getMyApplications(1, 1);
      const applicationsCount = applicationsResponse.pagination?.total || 0;
      
      // Load saved jobs count
      const savedJobsResponse = await savedJobsService.list(1, 1);
      const savedJobsCount = savedJobsResponse.pagination?.total || 0;
      
      // Count interviews (applications with 'reviewed' or 'accepted' status)
      const allApplicationsResponse = await applicationService.getMyApplications(1, 100);
      const interviewsCount = allApplicationsResponse.applications?.filter(app => 
        app.status === 'reviewed' || app.status === 'accepted'
      ).length || 0;
      
      setStats({
        applications: applicationsCount,
        interviews: interviewsCount,
        savedJobs: savedJobsCount,
        jobAlerts: 0 // Placeholder for future feature
      });
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Candidate Dashboard</h1>
        <p className="text-gray-600">Welcome back, {user?.username}</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="text-2xl font-bold text-primary-600">
            {loading ? '...' : stats.applications}
          </div>
          <div className="text-gray-600">Applications</div>
        </div>
        
        <div className="card">
          <div className="text-2xl font-bold text-green-600">
            {loading ? '...' : stats.interviews}
          </div>
          <div className="text-gray-600">Interviews</div>
        </div>
        
        <div className="card">
          <div className="text-2xl font-bold text-yellow-600">
            {loading ? '...' : stats.savedJobs}
          </div>
          <div className="text-gray-600">Saved Jobs</div>
        </div>
        
        <div className="card">
          <div className="text-2xl font-bold text-purple-600">
            {loading ? '...' : stats.jobAlerts}
          </div>
          <div className="text-gray-600">Job Alerts</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="flex flex-col gap-4">
            <Link to="/candidate/applications" className="btn-primary w-full text-sm py-2">
              View My Applications
            </Link>
            <Link to="/jobs" className="btn-secondary w-full text-sm py-2">
              Browse Jobs
            </Link>
            <Link to="/candidate/saved-jobs" className="btn-secondary w-full text-sm py-2">
              View Saved Jobs
            </Link>
            <Link to="/profile" className="btn-secondary w-full text-sm py-2">
              Manage Profile
            </Link>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Candidate Status</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">Candidate role active</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">Ready to browse jobs</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm">Application features in development</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateDashboard;

