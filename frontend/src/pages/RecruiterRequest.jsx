import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { recruiterService } from '../services/recruiterService';
import { authService } from '../services/authService';
import RecruiterRequestForm from '../components/forms/RecruiterRequestForm';
import Button from '../components/common/Button';

const RecruiterRequest = () => {
  const { user, token, isRecruiter } = useAuth();
  const navigate = useNavigate();
  const [requestStatus, setRequestStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [whoAmI, setWhoAmI] = useState(null);
  const [myRequests, setMyRequests] = useState([]);

  useEffect(() => {
    // Require fresh auth and always fetch latest status from backend on page open
    if (!token) {
      try {
        const path = window.location.pathname + window.location.search + window.location.hash;
        localStorage.setItem('returnTo', path);
      } catch {}
      navigate('/login');
      return;
    }
    fetchRequestStatus();
  }, [token, navigate]);

  const fetchRequestStatus = async () => {
    try {
      setLoading(true);
      // 1) Verify which user is being checked
      const meResp = await authService.getProfile();
      const me = meResp?.data?.user || meResp.user;
      setWhoAmI(me);

      // 2) Inspect actual DB state for this user
      let latestStatus = null;
      try {
        const listResp = await recruiterService.getMyRequests();
        const list = listResp?.data || [];
        setMyRequests(list);
        const pending = list.find(r => r.status === 'pending');
        if (pending) {
          latestStatus = { status: 'pending', message: 'Your request is under review' };
        }
      } catch (_) {
        // If listing is not available, continue with status endpoint
      }

      // Fallback to status endpoint if we didn't find a pending request
      if (!latestStatus) {
        const statusResp = await recruiterService.getMyStatus();
        latestStatus = statusResp?.data || null;
      }

      // If latest is approved/rejected or no_request, treat as no active request to allow form
      if (latestStatus && (
        latestStatus.status === 'approved' ||
        latestStatus.status === 'rejected' ||
        latestStatus.status === 'no_request'
      )) {
        setRequestStatus(null);
        setShowForm(true);
      } else {
        setRequestStatus(latestStatus);
      }
    } catch (error) {
      console.error('Failed to fetch request status:', error);
      if (error?.response?.status === 401) {
        try {
          const path = window.location.pathname + window.location.search + window.location.hash;
          localStorage.setItem('returnTo', path);
        } catch {}
        navigate('/login');
        return;
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCheckAndShowForm = async () => {
    // Always re-check status in DB before showing form
    try {
      setLoading(true);
      const response = await recruiterService.getMyStatus();
      const status = response?.data?.status;
      if (status === 'pending' || status === 'approved') {
        setRequestStatus(response.data);
        setShowForm(false);
      } else {
        setShowForm(true);
      }
    } catch (error) {
      if (error?.response?.status === 404) {
        // No existing request → allow form
        setShowForm(true);
      } else if (error?.response?.status === 401) {
        try {
          const path = window.location.pathname + window.location.search + window.location.hash;
          localStorage.setItem('returnTo', path);
        } catch {}
        navigate('/login');
      } else {
        // Fallback: allow form to proceed
        setShowForm(true);
      }
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

      {requestStatus && requestStatus.status !== 'no_request' ? (
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
            <Button onClick={handleCheckAndShowForm}>
              Submit Request
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecruiterRequest;
