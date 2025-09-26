import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { adminService } from '../../services/adminService';

const Profile = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [requesting, setRequesting] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [saving, setSaving] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [code, setCode] = useState('');
  const [form, setForm] = useState({ username: user?.username || '', email: user?.email || '' });
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');

  const onStartEdit = () => {
    setIsEditing(true);
    setMsg('');
    setErr('');
    setForm({ username: user?.username || '', email: user?.email || '' });
  };

  const requestCode = async () => {
    try {
      setRequesting(true);
      setMsg('');
      setErr('');
      await adminService.requestProfileCode();
      setCodeSent(true);
      setMsg('Verification code sent to your email.');
    } catch (e) {
      setErr('Failed to send verification code');
    } finally {
      setRequesting(false);
    }
  };

  const verifyCode = async () => {
    try {
      setVerifying(true);
      setMsg('');
      setErr('');
      await adminService.verifyProfileCode(code.trim());
      setMsg('Code verified. You can now save your changes.');
    } catch (e) {
      setErr('Invalid or expired code');
    } finally {
      setVerifying(false);
    }
  };

  const saveProfile = async () => {
    try {
      setSaving(true);
      setMsg('');
      setErr('');
      await adminService.updateProfile({ ...form, code: code.trim() });
      setMsg('Profile updated');
      setIsEditing(false);
    } catch (e) {
      setErr(e?.response?.data?.error || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
        <p className="text-gray-600">Manage your account information</p>
      </div>

      <div className="card">
        {msg ? <div className="mb-3 text-green-700 text-sm">{msg}</div> : null}
        {err ? <div className="mb-3 text-red-600 text-sm">{err}</div> : null}

        {!isEditing ? (
          <>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold">Username</h3>
                <p>{user?.username}</p>
              </div>
              <div>
                <h3 className="font-semibold">Email</h3>
                <p>{user?.email}</p>
              </div>
              <div>
                <h3 className="font-semibold">Roles</h3>
                <div className="flex space-x-2">
                  {user?.roles?.map((role, index) => (
                    <span key={index} className="bg-primary-100 text-primary-800 px-2 py-1 rounded text-sm">
                      {role.role}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="font-semibold">Email Verified</h3>
                <p>{user?.is_verified ? 'Yes' : 'No'}</p>
              </div>
              <div>
                <h3 className="font-semibold">Member Since</h3>
                <p>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}</p>
              </div>
            </div>
            <div className="mt-6 flex items-center justify-between gap-3">
              <button className="btn-secondary" onClick={onStartEdit}>Edit Profile</button>
              <Link to="/recruiter-request" className="btn-primary">Request Recruiter Access</Link>
            </div>
          </>
        ) : (
          <>
            <div className="space-y-4">
              <div>
                <label htmlFor="profile-username" className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input id="profile-username" className="w-full input" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
              </div>
              <div>
                <label htmlFor="profile-email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input id="profile-email" type="email" className="w-full input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </div>
              <div className="pt-2">
                {!codeSent ? (
                  <button className="btn-secondary" disabled={requesting} onClick={requestCode}>{requesting ? 'Sending…' : 'Send Verification Code'}</button>
                ) : (
                  <div className="space-y-3">
                    <div>
                      <label htmlFor="profile-code" className="block text-sm font-medium text-gray-700 mb-1">6-digit code</label>
                      <input id="profile-code" className="w-full input" value={code} onChange={(e) => setCode(e.target.value)} maxLength={6} />
                    </div>
                    <div className="flex items-center gap-3">
                      <button className="btn-secondary" onClick={verifyCode} disabled={verifying || !code}>{verifying ? 'Verifying…' : 'Verify Code'}</button>
                      <button className="btn-primary" onClick={saveProfile} disabled={saving || !code}>{saving ? 'Saving…' : 'Save Changes'}</button>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="mt-6 flex items-center justify-between gap-3">
              <button className="btn-light" onClick={() => setIsEditing(false)}>Cancel</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Profile;
