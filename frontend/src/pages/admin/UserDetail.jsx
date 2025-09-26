import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminService } from '../../services/adminService';

export default function UserDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [msg, setMsg] = useState('');
  const [form, setForm] = useState({ username: '', email: '', role: '' });

  const load = async (signal) => {
    setLoading(true);
    setError('');
    try {
      const res = await adminService.getUserById(id, { signal });
      const u = res.data;
      setForm({ username: u.username || '', email: u.email || '', role: (u.roles && u.roles[0]) || '' });
    } catch (e) {
      setError('Failed to load user');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    load(controller.signal);
    return () => controller.abort();
  }, [id]);

  const save = async () => {
    try {
      setMsg('');
      setError('');
      await adminService.updateUserById(id, form);
      setMsg('User updated');
    } catch (e) {
      setError(e?.response?.data?.error || 'Failed to update user');
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">User Detail</h1>
        <button className="btn-light" onClick={() => navigate(-1)}>Back</button>
      </div>
      {loading ? (
        <div className="card animate-pulse h-32" />
      ) : error ? (
        <div className="card text-red-600">{error}</div>
      ) : (
        <div className="card space-y-4">
          {msg ? <div className="text-green-700 text-sm">{msg}</div> : null}
          {error ? <div className="text-red-600 text-sm">{error}</div> : null}
          <div>
            <label htmlFor="ud-username" className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input id="ud-username" className="input w-full" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          </div>
          <div>
            <label htmlFor="ud-email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input id="ud-email" type="email" className="input w-full" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <div>
            <label htmlFor="ud-role" className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <select id="ud-role" className="input w-full" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="">(unchanged)</option>
              <option value="candidate">candidate</option>
              <option value="recruiter">recruiter</option>
              <option value="admin">admin</option>
            </select>
          </div>
          <div className="pt-2 flex items-center gap-3">
            <button className="btn-primary" onClick={save}>Save</button>
            <button className="btn-secondary" onClick={() => load()}>Reload</button>
          </div>
        </div>
      )}
    </div>
  );
}


