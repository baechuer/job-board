import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const JobDetail = () => {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [archiving, setArchiving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get(`/recruiter/my-jobs/${id}`);
        setJob(res?.data || res);
      } catch (e) {
        setError(e?.response?.data?.error || 'Failed to load job');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (loading) return <div className="max-w-3xl mx-auto">Loading...</div>;
  if (error) return <div className="max-w-3xl mx-auto text-red-600">{error}</div>;
  if (!job) return null;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-3">
        <button onClick={() => navigate(-1)} className="text-sm text-primary-600 hover:text-primary-700 hover:underline">← Back</button>
      </div>
      <div className="bg-white shadow-sm border border-gray-200 rounded-lg p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900">{job.title}</h1>
            <p className="text-sm text-gray-500 mt-1">Created {formatDate(job.created_at)}</p>
          </div>
          <div className="flex items-center gap-2">
            <button disabled={archiving} onClick={async () => {
              setArchiving(true);
              try {
                if (job.status === 'deprecated') {
                  await api.post(`/recruiter/my-jobs/${job.id}/unarchive`);
                } else {
                  await api.post(`/recruiter/my-jobs/${job.id}/archive`);
                }
                navigate('/recruiter/my-jobs');
              } catch (e) {
              } finally {
                setArchiving(false);
              }
            }} className="btn-secondary disabled:opacity-50">
              {archiving ? (job.status === 'deprecated' ? 'Unarchiving…' : 'Archiving…') : (job.status === 'deprecated' ? 'Unarchive Job' : 'Archive Job')}
            </button>
            <button onClick={() => navigate(`/recruiter/edit-job/${job.id}`)} className="btn-primary">Edit Job</button>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <InfoRow label="Location" value={job.location} />
          <InfoRow label="Type" value={humanize(job.employment_type)} />
          <InfoRow label="Seniority" value={humanize(job.seniority)} />
          <InfoRow label="Work Mode" value={humanize(job.work_mode)} />
          <InfoRow label="Status" value={humanize(job.status)} />
          <InfoRow label="Work Authorization" value={job.work_authorization} />
          <InfoRow label="Salary" value={`${job.salary_min} - ${job.salary_max}`} />
          <InfoRow label="Deadline" value={job.application_deadline?.slice(0,10) || '—'} />
        </div>

        <Section title="Description">
          <p className="whitespace-pre-wrap leading-relaxed text-gray-800">{job.description}</p>
        </Section>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Section title="Requirements">
            <ChipList items={job.requirements || []} />
          </Section>
          <Section title="Skills">
            <ChipList items={job.skills || []} />
          </Section>
        </div>

        <Section title="Responsibilities">
          <p className="whitespace-pre-wrap leading-relaxed text-gray-800">{job.responsibilities}</p>
        </Section>

        <Section title="Nice to haves">
          <p className="whitespace-pre-wrap leading-relaxed text-gray-800">{job.nice_to_haves || '—'}</p>
        </Section>

        <Section title="About team">
          <p className="whitespace-pre-wrap leading-relaxed text-gray-800">{job.about_team || '—'}</p>
        </Section>
      </div>
    </div>
  );
};

function humanize(value) {
  if (!value) return '—';
  return value.toString().split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function formatDate(value) {
  if (!value) return '—';
  try { return new Date(value).toLocaleDateString(); } catch { return value; }
}

export default JobDetail;

function InfoRow({ label, value }) {
  return (
    <div className="flex items-center justify-between bg-gray-50 rounded-md border border-gray-200 px-3 py-2 transition-colors hover:bg-gray-100">
      <div className="text-sm font-medium text-gray-600">{label}</div>
      <div className="text-sm text-gray-900">{value || '—'}</div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-2">{title}</h2>
      <div className="bg-white">{children}</div>
    </div>
  );
}

function ChipList({ items }) {
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? items : items.slice(0, 5);
  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {visible.map((text, idx) => (
          <span key={idx} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200 transition-colors hover:bg-gray-200 hover:border-gray-300 cursor-default">
            {text}
          </span>
        ))}
      </div>
      {items.length > 5 && (
        <button onClick={() => setExpanded(v => !v)} className="mt-3 text-sm text-primary-600 hover:text-primary-700 hover:underline">
          {expanded ? 'Show less' : `Show ${items.length - 5} more`}
        </button>
      )}
    </div>
  );
}


