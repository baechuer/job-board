import { useEffect, useRef, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import { useAuth } from '../../context/AuthContext';

const roleOptions = [
  { label: 'All (No Admins)', value: '' },
  { label: 'Candidates', value: 'candidate' },
  { label: 'Recruiters', value: 'recruiter' },
];

export default function Users() {
  const { isAdmin } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const role = searchParams.get('role') || '';
  const page = parseInt(searchParams.get('page') || '1', 10);

  const fetchUsers = async (signal) => {
    setLoading(true);
    try {
      const res = await adminService.listUsers({ role, page, per_page: 20, signal });
      setData(res.data);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    if (isAdmin()) fetchUsers(controller.signal);
    return () => controller.abort();
  }, [role, page]);

  const onRoleChange = (e) => {
    const next = new URLSearchParams(searchParams);
    if (e.target.value) next.set('role', e.target.value); else next.delete('role');
    next.set('page', '1');
    setSearchParams(next);
  };

  const changePage = (delta) => {
    const next = new URLSearchParams(searchParams);
    next.set('page', String(Math.max(1, page + delta)));
    setSearchParams(next);
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Manage Users</h1>
      </div>

      {/* Search/Filter bar styled like Jobs page */}
      <form className="bg-white border border-gray-200 rounded-xl shadow-sm p-4 flex flex-col sm:flex-row sm:items-center gap-3 mb-6">
        <div className="flex items-center w-full sm:flex-1">
          <span className="text-gray-400 mr-3" aria-hidden>👥</span>
          <select value={role} onChange={onRoleChange} className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
            {roleOptions.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </form>

      {loading ? (
        <div className="card animate-pulse h-32" />
      ) : error ? (
        <div className="card text-red-600">Failed to load users</div>
      ) : (
        <>
          {data?.users?.length === 0 ? (
            <div className="text-gray-500">No users found.</div>
          ) : (
            <>
              {/* Table view for md+ */}
              <div className="hidden md:block">
                <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">User</th>
                        <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">Email</th>
                        <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">Role</th>
                        <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">Joined</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 bg-white">
                      {data.users.map((u) => {
                        const name = u.username || u.email;
                        const initials = (name || '').split(/\s|\./).filter(Boolean).slice(0,2).map(s => s[0]?.toUpperCase()).join('') || 'U';
                        return (
                          <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-3">
                                <div className="h-9 w-9 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-sm font-semibold">{initials}</div>
                                <div className="">
                                  <div className="font-medium text-gray-900">{name}</div>
                                  {u.full_name ? (
                                    <div className="text-xs text-gray-500">{u.full_name}</div>
                                  ) : null}
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-gray-700">{u.email}</td>
                            <td className="px-6 py-4">
                              {u.role ? (
                                <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700 capitalize">{u.role}</span>
                              ) : (
                                <span className="text-xs text-gray-400">—</span>
                              )}
                            </td>
                            <td className="px-6 py-4 text-gray-700 text-sm">{u.created_at || ''}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Card list for mobile */}
              <div className="md:hidden space-y-3">
                {data.users.map((u) => {
                  const name = u.username || u.email;
                  const initials = (name || '').split(/\s|\./).filter(Boolean).slice(0,2).map(s => s[0]?.toUpperCase()).join('') || 'U';
                  return (
                    <div key={u.id} className="card transition-shadow hover:shadow-md hover:border-primary-200">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-sm font-semibold">{initials}</div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="text-base font-semibold text-gray-900">{name}</h3>
                              <p className="text-sm text-gray-600">{u.email}</p>
                            </div>
                            <div className="ml-3 text-right">
                              {u.role ? (
                                <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-[11px] font-medium text-gray-700 capitalize">{u.role}</span>
                              ) : null}
                              <div className="text-[11px] text-gray-400 mt-1">{u.created_at || ''}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}

          <div className="flex items-center justify-between mt-6">
            <button className="btn-secondary" onClick={() => changePage(-1)} disabled={page <= 1}>Prev</button>
            <div className="text-sm text-gray-600">Page {data?.pagination?.page} of {data?.pagination?.pages}</div>
            <button className="btn-secondary" onClick={() => changePage(1)} disabled={(data?.pagination?.page || 1) >= (data?.pagination?.pages || 1)}>Next</button>
          </div>
        </>
      )}
    </div>
  );
}


