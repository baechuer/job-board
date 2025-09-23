import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';

const MyJobs = () => {
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [perPage] = useState(20);
  const [showArchived, setShowArchived] = useState(false);
  const navigate = useNavigate();

  const status = showArchived ? 'deprecated' : 'active';

  const { data, isFetching, isError, error: queryError } = useQuery({
    queryKey: ['my-jobs', status, page, perPage],
    queryFn: async () => {
      const res = await api.get('/recruiter/my-jobs', { params: { page, per_page: perPage, status } });
      return res?.data || res;
    },
    keepPreviousData: true,
    staleTime: 60_000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: false,
  });

  useEffect(() => {
    setLoading(isFetching);
    setError(isError ? (queryError?.response?.data?.error || 'Failed to load jobs') : '');
    setPages(data?.pages || 1);
  }, [isFetching, isError, queryError, data]);

  useEffect(() => {
    if (status === 'active' && (data?.jobs?.length || 0) > 0) {
      queryClient.prefetchQuery({
        queryKey: ['my-jobs', 'deprecated', 1, perPage],
        queryFn: async () => {
          const res = await api.get('/recruiter/my-jobs', { params: { page: 1, per_page: perPage, status: 'deprecated' } });
          return res?.data || res;
        },
        staleTime: 60_000,
      });
    }
  }, [status, data, perPage, queryClient]);

  if (loading) return <div className="max-w-5xl mx-auto">Loading your jobs…</div>;
  if (error) return <div className="max-w-5xl mx-auto text-red-600">{error}</div>;

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">My Jobs</h1>
      <div className="flex items-center justify-between mb-4">
        <div className="text-sm text-gray-600">Showing {showArchived ? 'Archived' : 'Active'} Jobs</div>
        <button onClick={() => { setPage(1); setShowArchived(v => !v); }} className="btn-secondary">
          {showArchived ? 'Show Active' : 'Show Archived'}
        </button>
      </div>
      {(data?.jobs?.length || 0) === 0 ? (
        <div className="text-gray-600">{showArchived ? 'No archived jobs.' : "You haven't posted any jobs yet."}</div>
      ) : (
        <div className="overflow-hidden bg-white shadow-sm border border-gray-200 rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Salary</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deadline</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {(data?.jobs || []).map(job => (
                <tr key={job.id} className="cursor-pointer hover:bg-gray-50" onClick={() => navigate(`/recruiter/my-jobs/${job.id}`)}>
                  <td className="px-6 py-4 whitespace-nowrap">{job.title}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{job.location}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{humanize(job.employment_type) || '—'}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{formatDate(job.created_at)}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{humanize(job.status)}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{job.salary_min} - {job.salary_max}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{job.application_deadline?.slice(0,10) || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex items-center justify-between p-4 border-t border-gray-200">
            <button disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))} className="btn-secondary disabled:opacity-50">Previous</button>
            <div className="text-sm text-gray-600">Page {page} of {pages}</div>
            <button disabled={page >= pages} onClick={() => setPage(p => Math.min(pages, p + 1))} className="btn-secondary disabled:opacity-50">Next</button>
          </div>
        </div>
      )}
    </div>
  );
};

function humanize(value) {
  if (!value) return '—';
  return value
    .toString()
    .split('_')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function formatDate(value) {
  if (!value) return '—';
  try {
    const d = new Date(value);
    return d.toLocaleDateString();
  } catch {
    return value;
  }
}

export default MyJobs;


