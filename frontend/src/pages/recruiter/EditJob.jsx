import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../services/api';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';

const EditJob = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get(`/recruiter/my-jobs/${id}`);
        const data = res?.data || res;
        setForm({
          title: data.title || '',
          description: data.description || '',
          salary_min: data.salary_min ?? '',
          salary_max: data.salary_max ?? '',
          location: data.location || '',
          requirements: (data.requirements || []).join(', '),
          responsibilities: data.responsibilities || '',
          skills: (data.skills || []).join(', '),
          application_deadline: (data.application_deadline || '').slice(0,10),
          employment_type: data.employment_type || 'full_time',
          seniority: data.seniority || 'mid',
          work_mode: data.work_mode || 'onsite',
          visa_sponsorship: data.visa_sponsorship ? 'yes' : 'no',
          work_authorization: data.work_authorization || '',
          nice_to_haves: data.nice_to_haves || '',
          about_team: data.about_team || '',
        });
      } catch (e) {
        setError(e?.response?.data?.error || 'Failed to load job');
      }
    })();
  }, [id]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const toArray = (s) => s.split(',').map(x => x.trim()).filter(Boolean);

  const onSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = {
        ...form,
        salary_min: Number(form.salary_min),
        salary_max: Number(form.salary_max),
        requirements: toArray(form.requirements),
        skills: toArray(form.skills),
        visa_sponsorship: form.visa_sponsorship === 'yes',
      };
      await api.put(`/recruiter/my-jobs/${id}`, payload);
      navigate(`/recruiter/my-jobs/${id}`);
    } catch (e) {
      setError(e?.response?.data?.error || 'Failed to save job');
    } finally {
      setSaving(false);
    }
  };

  if (!form) return <div className="max-w-3xl mx-auto">Loading…</div>;

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Edit Job</h1>
      <form className="space-y-4" onSubmit={onSubmit}>
        <Input label="Title" name="title" value={form.title} onChange={handleChange} required />
        <Input label="Description" name="description" value={form.description} onChange={handleChange} required />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="Salary Min" name="salary_min" type="number" value={form.salary_min} onChange={handleChange} required />
          <Input label="Salary Max" name="salary_max" type="number" value={form.salary_max} onChange={handleChange} required />
        </div>
        <Input label="Location" name="location" value={form.location} onChange={handleChange} required />
        <Input label="Requirements (comma separated)" name="requirements" value={form.requirements} onChange={handleChange} />
        <Input label="Responsibilities" name="responsibilities" value={form.responsibilities} onChange={handleChange} />
        <Input label="Skills (comma separated)" name="skills" value={form.skills} onChange={handleChange} />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="employment_type" className="block text-sm font-medium text-gray-700 mb-1">Employment Type</label>
            <select id="employment_type" name="employment_type" value={form.employment_type} onChange={handleChange} className="input">
              <option value="full_time">Full-time</option>
              <option value="part_time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
              <option value="temporary">Temporary</option>
            </select>
          </div>
          <div>
            <label htmlFor="seniority" className="block text-sm font-medium text-gray-700 mb-1">Seniority</label>
            <select id="seniority" name="seniority" value={form.seniority} onChange={handleChange} className="input">
              <option value="intern">Intern</option>
              <option value="junior">Junior</option>
              <option value="mid">Mid</option>
              <option value="senior">Senior</option>
              <option value="lead">Lead</option>
            </select>
          </div>
          <div>
            <label htmlFor="work_mode" className="block text-sm font-medium text-gray-700 mb-1">Work Mode</label>
            <select id="work_mode" name="work_mode" value={form.work_mode} onChange={handleChange} className="input">
              <option value="onsite">On-site</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="Application Deadline" name="application_deadline" type="date" value={form.application_deadline} onChange={handleChange} />
          <div>
            <label htmlFor="visa_sponsorship" className="block text-sm font-medium text-gray-700 mb-1">Visa Sponsorship</label>
            <select id="visa_sponsorship" name="visa_sponsorship" value={form.visa_sponsorship} onChange={handleChange} className="input">
              <option value="no">No</option>
              <option value="yes">Yes</option>
            </select>
          </div>
        </div>
        <Input label="Work Authorization" name="work_authorization" value={form.work_authorization} onChange={handleChange} />
        <Input label="Nice to haves" name="nice_to_haves" value={form.nice_to_haves} onChange={handleChange} />
        <Input label="About team" name="about_team" value={form.about_team} onChange={handleChange} />
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <div className="flex items-center gap-3">
          <Button type="submit" loading={saving}>Save Changes</Button>
          <Button type="button" onClick={() => navigate(-1)} variant="secondary">Cancel</Button>
        </div>
      </form>
    </div>
  );
};

export default EditJob;


