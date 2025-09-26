import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../../services/api';

const ApplicationDetail = () => {
  const { applicationId } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [viewingFile, setViewingFile] = useState(null); // 'resume' or 'cover-letter'
  const [pdfContent, setPdfContent] = useState(null);

  useEffect(() => {
    fetchApplicationDetail();
  }, [applicationId]);

  const fetchApplicationDetail = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/applications/${applicationId}`);
      setApplication(response.data);
    } catch (err) {
      console.error('Error fetching application detail:', err);
      setError('Failed to load application details');
    } finally {
      setLoading(false);
    }
  };

  const updateApplicationStatus = async (newStatus) => {
    try {
      setUpdatingStatus(true);
      
      await api.patch(`/applications/${applicationId}/status`, {
        status: newStatus
      });
      
      // Update local state
      setApplication(prev => ({
        ...prev,
        status: newStatus,
        updated_at: new Date().toISOString()
      }));
      
    } catch (err) {
      console.error('Error updating application status:', err);
      alert('Failed to update application status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  const downloadFile = async (fileType) => {
    try {
      const response = await api.get(`/applications/${applicationId}/${fileType}`, {
        responseType: 'blob'
      });
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${application.first_name}_${application.last_name}_${fileType === 'resume' ? 'resume' : 'cover_letter'}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (err) {
      console.error(`Error downloading ${fileType}:`, err);
      alert(`Failed to download ${fileType === 'resume' ? 'resume' : 'cover letter'}`);
    }
  };

  const viewFileOnline = async (fileType) => {
    try {
      const response = await api.get(`/applications/${applicationId}/${fileType}/view`);
      setPdfContent(response.data);
      setViewingFile(fileType);
    } catch (err) {
      console.error(`Error viewing ${fileType}:`, err);
      alert(`Failed to view ${fileType === 'resume' ? 'resume' : 'cover letter'}`);
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

  const humanize = (value) => {
    if (!value) return '—';
    return value.toString().split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

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

  if (!application) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Application Not Found</h1>
          <p className="mt-2 text-gray-600">The application you're looking for doesn't exist.</p>
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
            <h1 className="text-3xl font-bold text-gray-900">Application Details</h1>
            <div className="mt-2">
              <Link 
                to={`/recruiter/jobs/${application.job.id}/applications`}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                ← Back to Applications
              </Link>
            </div>
          </div>
          <div className="text-right">
            <h2 className="text-xl font-semibold text-gray-900">{application.job.title}</h2>
            <p className="text-gray-600">{application.job.location}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Applicant Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h3 className="text-2xl font-bold text-gray-900">
                  {application.first_name} {application.last_name}
                </h3>
                <p className="text-gray-600">{application.email}</p>
              </div>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(application.status)}`}>
                {application.status}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <InfoRow label="Phone" value={application.phone} />
                <InfoRow label="Current Company" value={application.current_company} />
                <InfoRow label="Current Position" value={application.current_position} />
                <InfoRow label="Experience" value={application.experience} />
                <InfoRow label="Education" value={application.education} />
              </div>
              <div className="space-y-4">
                <InfoRow label="Applied Date" value={formatDate(application.created_at)} />
                <InfoRow label="Last Updated" value={formatDate(application.updated_at)} />
                <InfoRow label="Salary Expectation" value={application.salary_expectation ? `$${application.salary_expectation.toLocaleString()}` : null} />
                <InfoRow label="Notice Period" value={application.notice_period} />
                <InfoRow label="Work Authorization" value={application.work_authorization} />
              </div>
            </div>

            {application.skills && (
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {application.skills.split(',').map((skill, index) => (
                    <span key={index} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                      {skill.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {application.additional_info && (
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Additional Information</h4>
                <p className="text-gray-800 whitespace-pre-wrap">{application.additional_info}</p>
              </div>
            )}
          </div>

          {/* Links */}
          {(application.portfolio || application.linkedin || application.github) && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Links</h3>
              <div className="space-y-3">
                {application.portfolio && (
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-600 w-24">Portfolio:</span>
                    <a href={application.portfolio} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:text-primary-700 text-sm">
                      {application.portfolio}
                    </a>
                  </div>
                )}
                {application.linkedin && (
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-600 w-24">LinkedIn:</span>
                    <a href={application.linkedin} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:text-primary-700 text-sm">
                      {application.linkedin}
                    </a>
                  </div>
                )}
                {application.github && (
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-600 w-24">GitHub:</span>
                    <a href={application.github} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:text-primary-700 text-sm">
                      {application.github}
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Status Actions</h3>
            <div className="space-y-3">
              {application.status === 'submitted' && (
                <>
                  <button
                    onClick={() => updateApplicationStatus('reviewed')}
                    disabled={updatingStatus}
                    className="w-full px-4 py-2 text-sm bg-yellow-100 text-yellow-800 rounded-md hover:bg-yellow-200 disabled:opacity-50"
                  >
                    {updatingStatus ? 'Updating...' : 'Mark as Reviewing'}
                  </button>
                  <button
                    onClick={() => updateApplicationStatus('accepted')}
                    disabled={updatingStatus}
                    className="w-full px-4 py-2 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200 disabled:opacity-50"
                  >
                    {updatingStatus ? 'Updating...' : 'Accept'}
                  </button>
                  <button
                    onClick={() => updateApplicationStatus('rejected')}
                    disabled={updatingStatus}
                    className="w-full px-4 py-2 text-sm bg-red-100 text-red-800 rounded-md hover:bg-red-200 disabled:opacity-50"
                  >
                    {updatingStatus ? 'Updating...' : 'Reject'}
                  </button>
                </>
              )}
              {application.status === 'reviewed' && (
                <>
                  <button
                    onClick={() => updateApplicationStatus('accepted')}
                    disabled={updatingStatus}
                    className="w-full px-4 py-2 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200 disabled:opacity-50"
                  >
                    {updatingStatus ? 'Updating...' : 'Accept'}
                  </button>
                  <button
                    onClick={() => updateApplicationStatus('rejected')}
                    disabled={updatingStatus}
                    className="w-full px-4 py-2 text-sm bg-red-100 text-red-800 rounded-md hover:bg-red-200 disabled:opacity-50"
                  >
                    {updatingStatus ? 'Updating...' : 'Reject'}
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Documents */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Documents</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Resume</span>
                <div className="flex space-x-2">
                  <button
                    onClick={() => viewFileOnline('resume')}
                    className="px-3 py-1 text-xs bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200"
                  >
                    View Online
                  </button>
                  <button
                    onClick={() => downloadFile('resume')}
                    className="px-3 py-1 text-xs bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200"
                  >
                    Download
                  </button>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Cover Letter</span>
                <div className="flex space-x-2">
                  <button
                    onClick={() => viewFileOnline('cover-letter')}
                    className="px-3 py-1 text-xs bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200"
                  >
                    View Online
                  </button>
                  <button
                    onClick={() => downloadFile('cover-letter')}
                    className="px-3 py-1 text-xs bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200"
                  >
                    Download
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Job Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Information</h3>
            <div className="space-y-3">
              <InfoRow label="Title" value={application.job.title} />
              <InfoRow label="Location" value={application.job.location} />
              <InfoRow label="Type" value={humanize(application.job.employment_type)} />
              <InfoRow label="Seniority" value={humanize(application.job.seniority)} />
              <InfoRow label="Work Mode" value={humanize(application.job.work_mode)} />
              <InfoRow label="Salary Range" value={`$${application.job.salary_min.toLocaleString()} - $${application.job.salary_max.toLocaleString()}`} />
            </div>
          </div>
        </div>
      </div>

      {/* File Viewer Modal */}
      {viewingFile && pdfContent && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {viewingFile === 'resume' ? 'Resume' : 'Cover Letter'} - {application.first_name} {application.last_name}
                </h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => downloadFile(viewingFile === 'resume' ? 'resume' : 'cover-letter')}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                  >
                    Download
                  </button>
                  <button
                    onClick={() => {
                      setViewingFile(null);
                      setPdfContent(null);
                    }}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                  >
                    Close
                  </button>
                </div>
              </div>
              <div className="border border-gray-300 rounded-lg overflow-hidden">
                <iframe
                  src={`data:${pdfContent.mimetype};base64,${pdfContent.content}`}
                  width="100%"
                  height="600px"
                  style={{ border: 'none' }}
                  title={`${viewingFile === 'resume' ? 'Resume' : 'Cover Letter'} - ${application.first_name} ${application.last_name}`}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

function InfoRow({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm font-medium text-gray-600">{label}:</span>
      <span className="text-sm text-gray-900">{value || '—'}</span>
    </div>
  );
}

export default ApplicationDetail;
