import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import usePublicJob from '../../hooks/usePublicJob';
import { savedJobsService } from '../../services/savedJobsService';

const JobPublicDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { job, loading, error } = usePublicJob(id);

  const formatLabel = (val) => {
    if (!val || typeof val !== 'string') return val;
    const spaced = val.replace(/_/g, ' ');
    return spaced.replace(/\b\w/g, (m) => m.toUpperCase());
  };

  const [saved, setSaved] = useState(false);
  // Check saved status from backend when authenticated
  useEffect(() => {
    let active = true;
    (async () => {
      if (!user || !job?.id) return;
      try {
        const resp = await savedJobsService.getStatus(job.id);
        if (active) setSaved(!!(resp?.data?.saved));
      } catch {
        // fallback: do nothing
      }
    })();
    return () => { active = false; };
  }, [user, job?.id]);

  const toggleSaved = async () => {
    if (!job?.id) return;
    // If not logged in, route to login
    if (!user) {
      navigate('/login');
      return;
    }
    const optimistic = !saved;
    setSaved(optimistic);
    try {
      if (optimistic) {
        await savedJobsService.save(job.id);
      } else {
        await savedJobsService.unsave(job.id);
      }
    } catch {
      // revert on failure
      setSaved(!optimistic);
    }
  };

  const formatted = useMemo(() => {
    if (!job) return {};
    const fmtCurrency = (n) => {
      if (n === null || n === undefined || Number.isNaN(Number(n))) return null;
      try {
        return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(Number(n));
      } catch {
        return `$${Number(n).toLocaleString()}`;
      }
    };
    const fmtDate = (d) => {
      if (!d) return null;
      try { return new Date(d).toLocaleDateString(); } catch { return d; }
    };
    const salaryMin = fmtCurrency(job.salary_min);
    const salaryMax = fmtCurrency(job.salary_max);
    const salaryText = salaryMin && salaryMax ? `${salaryMin} - ${salaryMax}` : salaryMin || salaryMax || null;
    const deadlineText = fmtDate(job.application_deadline);
    return { salaryText, deadlineText };
  }, [job]);

  if (loading) return <div className="text-gray-500">Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!job) return <div className="text-gray-500">Job not found.</div>;

  return (
    <div className="max-w-6xl mx-auto">
      <button className="btn-secondary mb-4" onClick={() => navigate(-1)}>← Back</button>

      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-gray-600">
              {job.location && <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100 text-sm">📍 {job.location}</span>}
              {job.work_mode && <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-indigo-50 text-indigo-700 text-sm">🏠 {formatLabel(job.work_mode)}</span>}
              {job.employment_type && <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-emerald-50 text-emerald-700 text-sm">🗓 {formatLabel(job.employment_type)}</span>}
              {job.seniority && <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-amber-50 text-amber-700 text-sm">⭐ {formatLabel(job.seniority)}</span>}
            </div>
          </div>
          <div className="flex flex-col items-start md:items-end gap-2">
            {formatted.salaryText && (
              <div className="text-xl font-semibold text-gray-900">{formatted.salaryText}</div>
            )}
            {formatted.deadlineText && (
              <div className="text-sm text-gray-500">Apply by {formatted.deadlineText}</div>
            )}
            <div className="flex gap-2 mt-2">
              {!user ? (
                <Link to="/login" className="btn-primary">Apply Now</Link>
              ) : user.roles?.some(role => role.role === 'candidate') ? (
                <Link to={`/jobs/${job.id}/apply`} className="btn-primary">Apply Now</Link>
              ) : null}
              <button
                type="button"
                className="btn-secondary"
                onClick={toggleSaved}
                title={saved ? 'Remove from favorites' : 'Add to favorites'}
                aria-label={saved ? 'Remove from favorites' : 'Add to favorites'}
              >
                {saved ? '⭐ Saved' : '☆ Save job'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-3">About the role</h2>
            <p className="text-gray-800 whitespace-pre-line">{job.description}</p>
          </div>

          {Array.isArray(job.requirements) && job.requirements.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-3">Requirements</h3>
              <div className="flex flex-wrap gap-2">
                {job.requirements.map((r, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 rounded border border-gray-200 bg-white text-gray-800 text-xs transition-colors hover:bg-primary-50 hover:border-primary-200 hover:text-primary-800"
                  >
                    {r}
                  </span>
                ))}
              </div>
            </div>
          )}

          {Array.isArray(job.skills) && job.skills.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-3">Skills</h3>
              <div className="flex flex-wrap gap-2">
                {job.skills.map((s, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 rounded bg-gray-100 text-gray-700 text-xs transition-colors hover:bg-primary-50 hover:text-primary-800"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {job.nice_to_haves && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-3">Nice to haves</h3>
              <p className="text-gray-800 whitespace-pre-line">{job.nice_to_haves}</p>
            </div>
          )}

          {job.about_team && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-3">About the team</h3>
              <p className="text-gray-800 whitespace-pre-line">{job.about_team}</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <aside className="space-y-4">
          <div className="card">
            <h3 className="text-md font-semibold mb-3">Summary</h3>
              <div className="space-y-3 text-sm">
              <div className="flex items-start justify-between">
                <span className="text-gray-500">Location</span>
                <span className="text-gray-900">{job.location || '—'}</span>
              </div>
              <div className="flex items-start justify-between">
                <span className="text-gray-500">Work Mode</span>
                  <span className="text-gray-900">{job.work_mode ? formatLabel(job.work_mode) : '—'}</span>
              </div>
              <div className="flex items-start justify-between">
                <span className="text-gray-500">Employment</span>
                  <span className="text-gray-900">{job.employment_type ? formatLabel(job.employment_type) : '—'}</span>
              </div>
              <div className="flex items-start justify-between">
                <span className="text-gray-500">Seniority</span>
                  <span className="text-gray-900">{job.seniority ? formatLabel(job.seniority) : '—'}</span>
              </div>
              <div className="flex items-start justify-between">
                <span className="text-gray-500">Salary</span>
                <span className="text-gray-900">{formatted.salaryText || '—'}</span>
              </div>
              <div className="flex items-start justify-between">
                <span className="text-gray-500">Deadline</span>
                <span className="text-gray-900">{formatted.deadlineText || '—'}</span>
              </div>
              {job.visa_sponsorship !== undefined && (
                <div className="flex items-start justify-between">
                  <span className="text-gray-500">Visa Sponsorship</span>
                  <span className="text-gray-900">{job.visa_sponsorship ? 'Available' : 'Not available'}</span>
                </div>
              )}
              {job.work_authorization && (
                <div className="flex items-start justify-between">
                  <span className="text-gray-500">Work Authorization</span>
                  <span className="text-gray-900">{job.work_authorization}</span>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <h3 className="text-md font-semibold mb-3">Next steps</h3>
            {!user ? (
              <>
                <p className="text-gray-600 text-sm mb-3">Create an account or log in to apply and track your applications.</p>
                <div className="flex flex-col sm:flex-row gap-2">
                  <Link to="/login" className="btn-primary w-full">Log in to apply</Link>
                  <Link to="/register" className="btn-secondary w-full">Create account</Link>
                </div>
              </>
            ) : user.roles?.some(role => role.role === 'candidate') ? (
              <>
                <p className="text-gray-600 text-sm mb-3">You're signed in. Continue with your application.</p>
                <div className="flex flex-col sm:flex-row gap-2">
                  <Link to={`/jobs/${job.id}/apply`} className="btn-primary w-full">Apply Now</Link>
                  <button
                    type="button"
                    className="btn-secondary w-full"
                    onClick={toggleSaved}
                    title={saved ? 'Remove from favorites' : 'Add to favorites'}
                    aria-label={saved ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    {saved ? '⭐ Saved' : '☆ Save job'}
                  </button>
                </div>
              </>
            ) : (
              <>
                <p className="text-gray-600 text-sm mb-3">You're signed in as a recruiter. Switch to candidate account to apply for jobs.</p>
                <div className="flex flex-col sm:flex-row gap-2">
                  <button
                    type="button"
                    className="btn-secondary w-full"
                    onClick={toggleSaved}
                    title={saved ? 'Remove from favorites' : 'Add to favorites'}
                    aria-label={saved ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    {saved ? '⭐ Saved' : '☆ Save job'}
                  </button>
                </div>
              </>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
};

export default JobPublicDetail;



