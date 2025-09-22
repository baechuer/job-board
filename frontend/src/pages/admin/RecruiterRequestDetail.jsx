import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import Button from '../../components/common/Button';

const RecruiterRequestDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRequest();
  }, [id]);

  const fetchRequest = async () => {
    try {
      setLoading(true);
      // Reuse admin list and find the item client-side; alternatively, add a GET /admin/recruiter-requests/:id endpoint
      const resp = await adminService.getRecruiterRequests();
      const item = (resp?.data?.requests || []).find(r => String(r.id) === String(id));
      if (!item) {
        setError('Request not found');
      }
      setRequest(item || null);
    } catch (e) {
      setError('Failed to load request');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (notes) => {
    try {
      setActionLoading(true);
      await adminService.approveRequest(id, notes || 'Approved');
      navigate('/admin/recruiter-requests');
    } catch (e) {
      setError('Failed to approve');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (notes) => {
    try {
      setActionLoading(true);
      await adminService.rejectRequest(id, notes || 'Rejected');
      navigate('/admin/recruiter-requests');
    } catch (e) {
      setError('Failed to reject');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="card text-center text-red-600">{error}</div>
      </div>
    );
  }

  if (!request) {
    return null;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="card">
        <h1 className="text-2xl font-bold mb-2">Recruiter Request #{request.id}</h1>
        <div className="text-gray-600 mb-4">Submitted: {new Date(request.submitted_at).toLocaleString()}</div>
        <div className="space-y-2">
          <div><span className="font-semibold">User:</span> {request.user?.username} ({request.user?.email})</div>
          <div><span className="font-semibold">Status:</span> {request.status}</div>
          <div>
            <span className="font-semibold">Reason:</span>
            <div className="mt-2 whitespace-pre-wrap bg-gray-50 border border-gray-200 rounded p-3">{request.reason || '—'}</div>
          </div>
          {request.feedback && (
            <div>
              <span className="font-semibold">Feedback:</span>
              <div className="mt-2 whitespace-pre-wrap bg-gray-50 border border-gray-200 rounded p-3">{request.feedback}</div>
            </div>
          )}
        </div>
      </div>

      {request.status === 'pending' && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-3">Take Action</h2>
          <textarea
            id="adminNotes"
            placeholder="Add notes (optional)"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            rows="3"
          />
          <div className="flex gap-3 mt-4">
            <Button variant="primary" loading={actionLoading} onClick={() => handleApprove(document.getElementById('adminNotes').value)}>
              Approve
            </Button>
            <Button variant="danger" loading={actionLoading} onClick={() => handleReject(document.getElementById('adminNotes').value)}>
              Reject
            </Button>
            <Button variant="secondary" onClick={() => navigate('/admin/recruiter-requests')}>
              Back
            </Button>
          </div>
        </div>
      )}

      {request.status !== 'pending' && (
        <div className="card">
          <Button variant="secondary" onClick={() => navigate('/admin/recruiter-requests')}>Back to list</Button>
        </div>
      )}
    </div>
  );
};

export default RecruiterRequestDetail;
