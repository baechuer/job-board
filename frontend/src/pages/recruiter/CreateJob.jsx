import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import api from '../../services/api';

const CreateJob = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    title: '',
    description: '',
    salary_min: '',
    salary_max: '',
    location: '',
    requirements: '', // comma-separated
    responsibilities: '',
    skills: '', // comma-separated
    application_deadline: '', // YYYY-MM-DD
    // Job basics
    employment_type: 'full_time', // full_time, part_time, contract, internship, temporary
    seniority: 'mid', // intern, junior, mid, senior, lead
    work_mode: 'onsite', // onsite, remote, hybrid
    // Work authorization
    visa_sponsorship: 'no', // yes/no
    work_authorization: '',
    // Detailed content
    nice_to_haves: '',
    about_team: '',
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const toStringArray = (value) => value
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = {
        title: form.title.trim(),
        description: form.description.trim(),
        salary_min: Number(form.salary_min),
        salary_max: Number(form.salary_max),
        location: form.location.trim(),
        requirements: toStringArray(form.requirements),
        responsibilities: form.responsibilities.trim(),
        skills: toStringArray(form.skills),
        application_deadline: form.application_deadline,
        employment_type: form.employment_type,
        seniority: form.seniority,
        work_mode: form.work_mode,
        visa_sponsorship: form.visa_sponsorship === 'yes',
        work_authorization: form.work_authorization.trim(),
        nice_to_haves: form.nice_to_haves.trim(),
        about_team: form.about_team.trim(),
      };
      const res = await api.post('/recruiter/create-job', payload);
      if (res?.status === 201) {
        navigate('/dashboard/recruiter');
      }
    } catch (err) {
      const msg = err?.response?.data?.error || err?.response?.data?.message || 'Failed to create job';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Post Job</h1>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <Input label="Title" name="title" value={form.title} onChange={handleChange} required />
        <Input label="Description" name="description" value={form.description} onChange={handleChange} required />
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
          <Input label="Salary Min" name="salary_min" type="number" value={form.salary_min} onChange={handleChange} required />
          <Input label="Salary Max" name="salary_max" type="number" value={form.salary_max} onChange={handleChange} required />
        </div>
        <Input label="Location" name="location" value={form.location} onChange={handleChange} required />
        <Input label="Requirements (comma separated)" name="requirements" value={form.requirements} onChange={handleChange} required />
        <Input label="Responsibilities" name="responsibilities" value={form.responsibilities} onChange={handleChange} required />
        <Input label="Skills (comma separated)" name="skills" value={form.skills} onChange={handleChange} required />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="visa_sponsorship" className="block text-sm font-medium text-gray-700 mb-1">Visa Sponsorship</label>
            <select id="visa_sponsorship" name="visa_sponsorship" value={form.visa_sponsorship} onChange={handleChange} className="input">
              <option value="no">No</option>
              <option value="yes">Yes</option>
            </select>
          </div>
          <Input label="Work Authorization (e.g. US Citizen, H1B)" name="work_authorization" value={form.work_authorization} onChange={handleChange} />
        </div>
        <Input label="Nice to haves" name="nice_to_haves" value={form.nice_to_haves} onChange={handleChange} />
        <Input label="About team" name="about_team" value={form.about_team} onChange={handleChange} />
        <Input label="Application Deadline" name="application_deadline" type="date" value={form.application_deadline} onChange={handleChange} required />

        {error && <div className="text-red-600 text-sm">{error}</div>}

        <Button type="submit" loading={loading}>Post Job</Button>
      </form>
    </div>
  );
};

export default CreateJob;


