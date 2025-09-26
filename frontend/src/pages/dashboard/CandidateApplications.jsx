import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import applicationService from '../../services/applicationService';

const CandidateApplications = () => {
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [perPage] = useState(10);

  useEffect(() => {
    loadApplications();
  }, [page]);

  const loadApplications = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await applicationService.getMyApplications(page, perPage);
      setApplications(response.applications || []);
      setTotalPages(response.pagination?.pages || 1);
    } catch (err) {
      console.error('Failed to load applications:', err);
      setError('Failed to load applications. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'submitted':
        return 'bg-blue-100 text-blue-800 border border-blue-200';
      case 'reviewed':
        return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
      case 'accepted':
        return 'bg-green-100 text-green-800 border border-green-200';
      case 'rejected':
        return 'bg-red-100 text-red-800 border border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border border-gray-200';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatSalary = (job) => {
    if (job.salary_min && job.salary_max) {
      return `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`;
    }
    return 'Salary not specified';
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your applications...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-8">
          <div className="text-red-600 mb-4">{error}</div>
          <button 
            onClick={loadApplications}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Applications</h1>
        <p className="text-gray-600">Track your job applications and their status</p>
      </div>

      {applications.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📝</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No applications yet</h3>
          <p className="text-gray-600 mb-6">Start applying to jobs to see your applications here.</p>
          <Link to="/jobs" className="btn-primary">
            Browse Jobs
          </Link>
        </div>
      ) : (
        <>
          {/* Scrollable Applications Container */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Your Applications ({applications.length})</h2>
            </div>
            
            {/* Scrollable Applications List */}
            <div className="max-h-96 overflow-y-auto">
              <div className="divide-y divide-gray-200">
                {applications.map((application) => (
                  <div key={application.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      {/* Left side - Job Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                              <Link 
                                to={`/jobs/${application.job?.id}`}
                                className="hover:text-primary-600 transition-colors"
                              >
                                {application.job?.title || 'Job Title Not Available'}
                              </Link>
                            </h3>
                            
                            {/* Job Details Row */}
                            <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
                              <span className="flex items-center">
                                <span className="text-pink-500 mr-1">📍</span>
                                {application.job?.location || 'Location not specified'}
                              </span>
                              <span className="flex items-center">
                                <span className="text-amber-600 mr-1">💼</span>
                                {application.job?.employment_type?.replace('_', ' ') || 'Employment type not specified'}
                              </span>
                              <span className="flex items-center">
                                <span className="text-blue-500 mr-1">🏢</span>
                                {application.job?.work_mode || 'Work mode not specified'}
                              </span>
                            </div>
                            
                            {/* Salary */}
                            <div className="flex items-center text-sm text-gray-600 mb-3">
                              <span className="text-yellow-500 mr-1">💰</span>
                              {formatSalary(application.job)}
                            </div>
                            
                            {/* Applicant Info */}
                            <div className="text-sm text-gray-600 space-y-1">
                              <p><span className="font-medium">Applied as:</span> {application.first_name} {application.last_name}</p>
                              <p><span className="font-medium">Email:</span> {application.email}</p>
                              {application.phone && <p><span className="font-medium">Phone:</span> {application.phone}</p>}
                            </div>
                          </div>
                          
                          {/* Right side - Status and Actions */}
                          <div className="flex flex-col items-end ml-4">
                            {/* Status Badge */}
                            <div className="mb-3">
                              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(application.status)}`}>
                                {application.status}
                              </span>
                            </div>
                            
                            {/* Applied Date */}
                            <div className="text-xs text-gray-500 mb-3">
                              Applied {formatDate(application.applied_at)}
                            </div>
                            
                            {/* Action Button */}
                            <Link 
                              to={`/jobs/${application.job?.id}`}
                              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
                            >
                              View Job
                            </Link>
                            
                            {/* Success Message */}
                            {application.status === 'submitted' && (
                              <div className="text-xs text-green-600 mt-2 text-center">
                                Application submitted successfully
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              
              <span className="text-sm text-gray-600">
                Page {page} of {totalPages}
              </span>
              
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}

          {/* Quick Actions */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link to="/jobs" className="card hover:shadow-md transition-shadow text-center">
              <div className="text-2xl mb-2">🔍</div>
              <h3 className="font-semibold text-gray-900">Browse Jobs</h3>
              <p className="text-sm text-gray-600">Find new opportunities</p>
            </Link>
            
            <Link to="/candidate/saved-jobs" className="card hover:shadow-md transition-shadow text-center">
              <div className="text-2xl mb-2">⭐</div>
              <h3 className="font-semibold text-gray-900">Saved Jobs</h3>
              <p className="text-sm text-gray-600">View your saved jobs</p>
            </Link>
            
            <Link to="/profile" className="card hover:shadow-md transition-shadow text-center">
              <div className="text-2xl mb-2">👤</div>
              <h3 className="font-semibold text-gray-900">Update Profile</h3>
              <p className="text-sm text-gray-600">Keep your profile current</p>
            </Link>
          </div>
        </>
      )}
    </div>
  );
};

export default CandidateApplications;
