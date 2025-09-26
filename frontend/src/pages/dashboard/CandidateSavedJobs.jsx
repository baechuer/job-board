import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { savedJobsService } from '../../services/savedJobsService';

const CandidateSavedJobs = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const resp = await savedJobsService.list(1, 100);
        setItems(resp?.data?.items || []);
      } catch (e) {
        setError('Failed to load saved jobs');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="text-gray-500">Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">My Saved Jobs</h1>
      {items.length === 0 ? (
        <div className="text-gray-500">You have no saved jobs yet.</div>
      ) : (
        <div className="space-y-3">
          {items.map((it, idx) => (
            <div key={idx} className="card cursor-pointer transition-shadow hover:shadow-md hover:border-primary-200" onClick={() => navigate(`/jobs/${it.job_id}`)}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">{it.title}</h3>
                  <p className="text-gray-600 text-sm">{it.location} {it.work_mode ? `• ${it.work_mode}` : ''}</p>
                  {Array.isArray(it.skills) && it.skills.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {it.skills.slice(0,6).map((s, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs">{s}</span>
                      ))}
                    </div>
                  )}
                  <div className="text-sm text-gray-500 mt-2">Saved on {new Date(it.saved_at).toLocaleDateString()}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CandidateSavedJobs;


