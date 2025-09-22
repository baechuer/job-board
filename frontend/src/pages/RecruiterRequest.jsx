import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { recruiterService } from '../services/recruiterService';
import RecruiterRequestForm from '../components/forms/RecruiterRequestForm';
import Button from '../components/common/Button';

const RecruiterRequest = () => {
  const { user, isRecruiter } = useAuth();
  const [requestStatus, setRequestStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    if (user && !isRecruiter()) {
      fetchRequestStatus();
    } else {
      setLoading(false);
    }
  }, [user, isRecruiter]);

  const fetchRequestStatus = async () => {
    try {
      const response = await recruiterService.getMyStatus();
      setRequestStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch request status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuccess = () => {
    setShowForm(false);
    fetchRequestStatus();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (isRecruiter()) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center">
          <div className="text-green-500 text-6xl mb-4">✓</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">You're Already a Recruiter!</h1>
          <p className="text-gray-600 mb-6">
            You have recruiter access and can post jobs (coming soon).
          </p>
          <Button onClick={() => window.history.back()}>
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Request Recruiter Access</h1>
        <p className="text-gray-600">Submit a request to become a recruiter</p>
      </div>

      {requestStatus ? (
        <div className="card">
          <div className="text-center">
            <div className={`text-6xl mb-4 ${
              requestStatus.status === 'approved' ? 'text-green-500' :
              requestStatus.status === 'rejected' ? 'text-red-500' :
              'text-yellow-500'
            }`}>
              {requestStatus.status === 'approved' ? '✓' :
               requestStatus.status === 'rejected' ? '✗' :
               '⏳'}
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {requestStatus.status === 'approved' ? 'Request Approved!' :
               requestStatus.status === 'rejected' ? 'Request Rejected' :
               'Request Pending'}
            </h2>
            <p className="text-gray-600 mb-6">
              {requestStatus.message}
            </p>
            <Button onClick={() => window.history.back()}>
              Go Back
            </Button>
          </div>
        </div>
      ) : showForm ? (
        <div className="card">
          <RecruiterRequestForm onSuccess={handleSuccess} onCancel={() => setShowForm(false)} />
        </div>
      ) : (
        <div className="card">
          <div className="text-center">
            <h2 className="text-xl font-semibold mb-4">Submit Recruiter Request</h2>
            <p className="text-gray-600 mb-6">
              Request access to post jobs and manage applications as a recruiter.
            </p>
            <Button onClick={() => setShowForm(true)}>
              Submit Request
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecruiterRequest;
