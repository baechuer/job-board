import { useEffect, useRef, useState } from 'react';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';
import useDebouncedValue from '../../hooks/useDebouncedValue';

const defaultFetcher = async ({ q, page, perPage, signal }) => {
  const resp = await api.get('/recruiter/jobs', { params: { q: q || undefined, page, per_page: perPage }, signal });
  return resp?.data || { jobs: [], pages: 1, current_page: 1, total: 0 };
};

const Jobs = ({ fetcher = defaultFetcher }) => {
  const [q, setQ] = useState('');
  const [page, setPage] = useState(1);
  const navigate = useNavigate();
  const [perPage] = useState(10);
  const [data, setData] = useState({ jobs: [], pages: 1, current_page: 1, total: 0 });
  const [loading, setLoading] = useState(false);

  const fetchJobs = async (query, pageNum, signal) => {
    setLoading(true);
    try {
      const result = await fetcher({ q: query, page: pageNum, perPage, signal });
      setData(result || { jobs: [], pages: 1, current_page: 1, total: 0 });
    } catch (err) {
      if (err?.name !== 'CanceledError' && err?.code !== 'ERR_CANCELED') {
        // swallow other errors lightly for now
      }
    } finally {
      setLoading(false);
    }
  };

  const didMountRef = useRef(false);
  useEffect(() => {
    const controller = new AbortController();
    if (didMountRef.current) {
      fetchJobs(q, page, controller.signal);
    } else {
      didMountRef.current = true; // initial render handled by debounced effect
    }
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  // Debounced search
  const dq = useDebouncedValue(q, 300);
  useEffect(() => {
    setPage(1);
    const controller = new AbortController();
    if (dq.length === 0 || dq.length >= 2) {
      fetchJobs(dq, 1, controller.signal);
    }
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dq]);

  const onSearch = (e) => {
    e.preventDefault();
    setPage(1);
    const controller = new AbortController();
    fetchJobs(q, 1, controller.signal);
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-3">Browse Jobs</h1>
        {/* Prominent search bar */}
        <form onSubmit={onSearch} className="bg-white border border-gray-200 rounded-xl shadow-sm p-4 flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="flex items-center w-full sm:flex-1">
            <span className="text-gray-400 mr-3" aria-hidden>🔎</span>
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by job title or skills (e.g. React, Python)"
              aria-label="Search jobs by title or skills"
              className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          {q && (
            <button type="button" onClick={() => { setQ(''); setPage(1); const c=new AbortController(); fetchJobs('', 1, c.signal); }} className="btn-secondary w-full sm:w-auto">Clear</button>
          )}
          <button className="btn-primary w-full sm:w-auto" type="submit">Search</button>
        </form>
        <p className="text-gray-500 text-sm mt-2">Tip: Try keywords like “Senior”, “Remote”, or a skill.</p>
      </div>

      <div className="space-y-3">
        {loading ? (
          <div className="text-gray-500">Loading...</div>
        ) : data.jobs.length === 0 ? (
          <div className="text-gray-500">No jobs found.</div>
        ) : (
          data.jobs.map((job) => (
            <div
              key={job.id}
              className="card cursor-pointer transition-shadow hover:shadow-md hover:border-primary-200"
              onClick={() => navigate(`/jobs/${job.id}`)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">{job.title}</h3>
                  <p className="text-gray-600 text-sm">{job.location} {job.work_mode ? `• ${job.work_mode}` : ''}</p>
                  {Array.isArray(job.skills) && job.skills.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {job.skills.slice(0,6).map((s, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs">{s}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="flex items-center justify-between mt-6">
        <button disabled={page<=1} onClick={() => setPage((p)=>p-1)} className="btn-secondary disabled:opacity-50">Prev</button>
        <div className="text-sm text-gray-600">Page {data.current_page} of {data.pages}</div>
        <button disabled={data.current_page>=data.pages} onClick={() => setPage((p)=>p+1)} className="btn-secondary disabled:opacity-50">Next</button>
      </div>
    </div>
  );
};

export default Jobs;



