import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const JobApplications = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [updatingStatus, setUpdatingStatus] = useState(null);

  const statusOptions = [
    { value: 'all', label: 'All Applications', count: 0 },
    { value: 'submitted', label: 'Submitted', count: 0 },
    { value: 'reviewed', label: 'Under Review', count: 0 },
    { value: 'accepted', label: 'Accepted', count: 0 },
    { value: 'rejected', label: 'Rejected', count: 0 }
  ];

  useEffect(() => {
    fetchJobAndApplications();
  }, [jobId]);

  const fetchJobAndApplications = async () => {
    try {
      setLoading(true);
      
      // Fetch job details
      const jobResponse = await api.get(`/recruiter/my-jobs/${jobId}`);
      setJob(jobResponse.data);
      
      // Fetch applications for this job
      const applicationsResponse = await api.get(`/applications/jobs/${jobId}/applications`);
      setApplications(applicationsResponse.data.applications || []);
      
    } catch (err) {
      console.error('Error fetching job applications:', err);
      setError('Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  const updateApplicationStatus = async (applicationId, newStatus) => {
    try {
      setUpdatingStatus(applicationId);
      
      await api.patch(`/applications/${applicationId}/status`, {
        status: newStatus
      });
      
      // Update local state
      setApplications(prev => 
        prev.map(app => 
          app.id === applicationId 
            ? { ...app, status: newStatus, updated_at: new Date().toISOString() }
            : app
        )
      );
      
    } catch (err) {
      console.error('Error updating application status:', err);
      alert('Failed to update application status');
    } finally {
      setUpdatingStatus(null);
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
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredApplications = applications.filter(app => 
    statusFilter === 'all' || app.status.toLowerCase() === statusFilter
  );

  // Calculate status counts
  const statusCounts = statusOptions.map(option => ({
    ...option,
    count: option.value === 'all' 
      ? applications.length 
      : applications.filter(app => app.status.toLowerCase() === option.value).length
  }));

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Job Not Found</h1>
          <p className="mt-2 text-gray-600">The job you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Job Applications</h1>
            <div className="mt-2">
              <Link 
                to={`/recruiter/my-jobs/${jobId}`}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                ← Back to Job Details
              </Link>
            </div>
          </div>
          <div className="text-right">
            <h2 className="text-xl font-semibold text-gray-900">{job.title}</h2>
            <p className="text-gray-600">{job.location}</p>
          </div>
        </div>
      </div>

      {/* Status Filter Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {statusCounts.map((option) => (
              <button
                key={option.value}
                onClick={() => setStatusFilter(option.value)}
                className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  statusFilter === option.value
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {option.label}
                <span className={`ml-2 py-0.5 px-2 rounded-full text-xs ${
                  statusFilter === option.value
                    ? 'bg-primary-100 text-primary-600'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {option.count}
                </span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Applications List */}
      <div className="space-y-4">
        {filteredApplications.length === 0 ? (
          <div className="text-center py-12">
            <div className="mx-auto h-12 w-12 text-gray-400">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No applications</h3>
            <p className="mt-1 text-sm text-gray-500">
              {statusFilter === 'all' 
                ? 'No applications have been submitted for this job yet.'
                : `No applications with status "${statusFilter}".`
              }
            </p>
          </div>
        ) : (
          filteredApplications.map((application) => (
            <div key={application.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {application.first_name} {application.last_name}
                    </h3>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(application.status)}`}>
                      {application.status}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Email:</span> {application.email}
                      </p>
                      {application.phone && (
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Phone:</span> {application.phone}
                        </p>
                      )}
                      {application.current_company && (
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Current Company:</span> {application.current_company}
                        </p>
                      )}
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Applied:</span> {formatDate(application.applied_at)}
                      </p>
                      {application.experience && (
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Experience:</span> {application.experience}
                        </p>
                      )}
                      {application.salary_expectation && (
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Salary Expectation:</span> ${application.salary_expectation.toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>

                  {application.additional_info && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Additional Info:</span>
                      </p>
                      <p className="text-sm text-gray-800 mt-1">{application.additional_info}</p>
                    </div>
                  )}
                </div>

                <div className="flex flex-col space-y-2 ml-6">
                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    {application.status === 'submitted' && (
                      <>
                        <button
                          onClick={() => updateApplicationStatus(application.id, 'reviewed')}
                          disabled={updatingStatus === application.id}
                          className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-md hover:bg-yellow-200 disabled:opacity-50"
                        >
                          {updatingStatus === application.id ? 'Updating...' : 'Mark as Reviewing'}
                        </button>
                        <button
                          onClick={() => updateApplicationStatus(application.id, 'accepted')}
                          disabled={updatingStatus === application.id}
                          className="px-3 py-1 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200 disabled:opacity-50"
                        >
                          {updatingStatus === application.id ? 'Updating...' : 'Accept'}
                        </button>
                        <button
                          onClick={() => updateApplicationStatus(application.id, 'rejected')}
                          disabled={updatingStatus === application.id}
                          className="px-3 py-1 text-sm bg-red-100 text-red-800 rounded-md hover:bg-red-200 disabled:opacity-50"
                        >
                          {updatingStatus === application.id ? 'Updating...' : 'Reject'}
                        </button>
                      </>
                    )}
                    {application.status === 'reviewed' && (
                      <>
                        <button
                          onClick={() => updateApplicationStatus(application.id, 'accepted')}
                          disabled={updatingStatus === application.id}
                          className="px-3 py-1 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200 disabled:opacity-50"
                        >
                          {updatingStatus === application.id ? 'Updating...' : 'Accept'}
                        </button>
                        <button
                          onClick={() => updateApplicationStatus(application.id, 'rejected')}
                          disabled={updatingStatus === application.id}
                          className="px-3 py-1 text-sm bg-red-100 text-red-800 rounded-md hover:bg-red-200 disabled:opacity-50"
                        >
                          {updatingStatus === application.id ? 'Updating...' : 'Reject'}
                        </button>
                      </>
                    )}
                  </div>

                  {/* View Application Button */}
                  <button
                    onClick={() => navigate(`/recruiter/applications/${application.id}`)}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                  >
                    View Full Application
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default JobApplications;
