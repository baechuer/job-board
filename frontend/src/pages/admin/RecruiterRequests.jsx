import { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import Button from '../../components/common/Button';

const RecruiterRequests = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const response = await adminService.getRecruiterRequests();
      setRequests(response.data.requests || []);
    } catch (error) {
      console.error('Failed to fetch requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId, notes) => {
    try {
      setActionLoading(true);
      await adminService.approveRequest(requestId, notes);
      await fetchRequests(); // Refresh the list
      setSelectedRequest(null);
    } catch (error) {
      console.error('Failed to approve request:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (requestId, notes) => {
    try {
      setActionLoading(true);
      await adminService.rejectRequest(requestId, notes);
      await fetchRequests(); // Refresh the list
      setSelectedRequest(null);
    } catch (error) {
      console.error('Failed to reject request:', error);
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

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Recruiter Requests</h1>
        <p className="text-gray-600">Manage recruiter access requests</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="text-2xl font-bold text-yellow-600">
            {requests.filter(r => r.status === 'pending').length}
          </div>
          <div className="text-gray-600">Pending</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-green-600">
            {requests.filter(r => r.status === 'approved').length}
          </div>
          <div className="text-gray-600">Approved</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-red-600">
            {requests.filter(r => r.status === 'rejected').length}
          </div>
          <div className="text-gray-600">Rejected</div>
        </div>
      </div>

      {/* Requests List */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Submitted
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {requests.map((request) => (
                <tr key={request.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {request.user?.username || 'Unknown User'}
                      </div>
                      <div className="text-sm text-gray-500">
                        {request.user?.email || 'No email'}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      request.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      request.status === 'approved' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {request.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(request.submitted_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {request.status === 'pending' && (
                      <div className="space-x-2">
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => setSelectedRequest({ ...request, action: 'approve' })}
                        >
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => setSelectedRequest({ ...request, action: 'reject' })}
                        >
                          Reject
                        </Button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Modal */}
      {selectedRequest && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {selectedRequest.action === 'approve' ? 'Approve Request' : 'Reject Request'}
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                User: {selectedRequest.user?.username} ({selectedRequest.user?.email})
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Reason: {selectedRequest.reason}
              </p>
              <textarea
                placeholder={`Add notes for ${selectedRequest.action}...`}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows="3"
              />
              <div className="flex space-x-3 mt-4">
                <Button
                  variant={selectedRequest.action === 'approve' ? 'primary' : 'danger'}
                  loading={actionLoading}
                  onClick={() => {
                    const notes = document.querySelector('textarea').value;
                    if (selectedRequest.action === 'approve') {
                      handleApprove(selectedRequest.id, notes);
                    } else {
                      handleReject(selectedRequest.id, notes);
                    }
                  }}
                >
                  {selectedRequest.action === 'approve' ? 'Approve' : 'Reject'}
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => setSelectedRequest(null)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecruiterRequests;
