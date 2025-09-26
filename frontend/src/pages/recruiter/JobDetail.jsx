import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const JobDetail = () => {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [archiving, setArchiving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
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

  const handleDeleteJob = async () => {
    setDeleting(true);
    try {
      const response = await api.delete(`/recruiter/my-jobs/${job.id}`);
      console.log('Job deletion summary:', response.data.deletion_summary);
      
      // Show success message and navigate
      alert(`Job "${job.title}" has been permanently deleted.\n\nDeletion Summary:\n- Applications deleted: ${response.data.deletion_summary.applications_deleted}\n- Files deleted: ${response.data.deletion_summary.file_cleanup.files_deleted}\n- Folders deleted: ${response.data.deletion_summary.file_cleanup.folders_deleted}`);
      
      navigate('/recruiter/my-jobs');
    } catch (e) {
      setError(e?.response?.data?.error || 'Failed to delete job');
      setShowDeleteModal(false);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <div className="max-w-3xl mx-auto">Loading...</div>;
  if (error) return <div className="max-w-3xl mx-auto text-red-600">{error}</div>;
  if (!job) return null;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-3">
        <button onClick={() => navigate(-1)} className="text-sm text-primary-600 hover:text-primary-700 hover:underline">← Back</button>
      </div>
      <div className="bg-white shadow-sm border border-gray-200 rounded-lg p-6">
        {/* Header Section */}
        <div className="mb-6">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
          <p className="text-sm text-gray-500">Created {formatDate(job.created_at)}</p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3 mb-6">
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
          }} className="btn-secondary disabled:opacity-50 whitespace-nowrap">
            {archiving ? (job.status === 'deprecated' ? 'Unarchiving…' : 'Archiving…') : (job.status === 'deprecated' ? 'Unarchive Job' : 'Archive Job')}
          </button>
          <button onClick={() => navigate(`/recruiter/jobs/${job.id}/applications`)} className="btn-primary whitespace-nowrap">View Applications</button>
          <button onClick={() => navigate(`/recruiter/edit-job/${job.id}`)} className="btn-secondary whitespace-nowrap">Edit Job</button>
          <button 
            onClick={() => setShowDeleteModal(true)}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap"
          >
            Delete Job
          </button>
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

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="mt-2 text-center">
                <h3 className="text-lg font-medium text-gray-900">Delete Job</h3>
                <div className="mt-2 px-7 py-3">
                  <p className="text-sm text-gray-500">
                    Are you sure you want to permanently delete <strong>"{job.title}"</strong>?
                  </p>
                  <p className="text-sm text-red-600 mt-2">
                    This action cannot be undone. This will delete:
                  </p>
                  <ul className="text-sm text-gray-600 mt-1 text-left">
                    <li>• The job posting</li>
                    <li>• All applications for this job</li>
                    <li>• All resume and cover letter files</li>
                    <li>• All saved job records</li>
                  </ul>
                </div>
              </div>
              <div className="flex space-x-3 mt-4">
                <button
                  onClick={handleDeleteJob}
                  disabled={deleting}
                  className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  {deleting ? 'Deleting...' : 'Yes, Delete Job'}
                </button>
                <button
                  onClick={() => setShowDeleteModal(false)}
                  disabled={deleting}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 disabled:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
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


