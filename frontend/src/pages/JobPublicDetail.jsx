import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

const JobPublicDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const resp = await api.get(`/recruiter/jobs/${id}`);
        if (mounted) setJob(resp.data);
      } catch (e) {
        if (mounted) setError('Job not found');
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [id]);

  if (loading) return <div className="text-gray-500">Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <button className="btn-secondary mb-4" onClick={() => navigate(-1)}>← Back</button>
      <div className="card">
        <h1 className="text-2xl font-bold mb-2">{job.title}</h1>
        <p className="text-gray-600 mb-4">{job.location} {job.work_mode ? `• ${job.work_mode}` : ''}</p>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <div className="text-sm text-gray-500">Employment Type</div>
            <div>{job.employment_type || '—'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Seniority</div>
            <div>{job.seniority || '—'}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Salary Range</div>
            <div>{job.salary_min} - {job.salary_max}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Application Deadline</div>
            <div>{job.application_deadline || '—'}</div>
          </div>
        </div>

        <h2 className="font-semibold mb-2">Description</h2>
        <p className="text-gray-800 whitespace-pre-line mb-6">{job.description}</p>

        {Array.isArray(job.requirements) && job.requirements.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Requirements</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-800">
              {job.requirements.map((r, idx) => <li key={idx}>{r}</li>)}
            </ul>
          </div>
        )}

        {Array.isArray(job.skills) && job.skills.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Skills</h3>
            <div className="flex flex-wrap gap-2">
              {job.skills.map((s, idx) => (
                <span key={idx} className="px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs">{s}</span>
              ))}
            </div>
          </div>
        )}

        {job.nice_to_haves && (
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Nice to haves</h3>
            <p className="text-gray-800 whitespace-pre-line">{job.nice_to_haves}</p>
          </div>
        )}

        {job.about_team && (
          <div className="mb-2">
            <h3 className="font-semibold mb-2">About the team</h3>
            <p className="text-gray-800 whitespace-pre-line">{job.about_team}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobPublicDetail;


