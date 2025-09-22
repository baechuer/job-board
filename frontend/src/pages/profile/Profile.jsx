import { useAuth } from '../../context/AuthContext';

const Profile = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
        <p className="text-gray-600">Manage your account information</p>
      </div>

      <div className="card">
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
        <div className="mt-6">
          <p className="text-gray-500 text-sm">Profile editing features coming soon...</p>
        </div>
      </div>
    </div>
  );
};

export default Profile;
