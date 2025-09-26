import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Login from './pages/auth/Login';
import ForgotPassword from './pages/auth/ForgotPassword';
import Register from './pages/auth/Register';
import VerifyEmail from './pages/auth/VerifyEmail';
import ResetPassword from './pages/auth/ResetPassword';
import AdminDashboard from './pages/dashboard/AdminDashboard';
import RecruiterDashboard from './pages/dashboard/RecruiterDashboard';
import CandidateDashboard from './pages/dashboard/CandidateDashboard';
import CandidateSavedJobs from './pages/dashboard/CandidateSavedJobs';
import CandidateApplications from './pages/dashboard/CandidateApplications';
import Jobs from './pages/jobs/Jobs';
import JobPublicDetail from './pages/jobs/JobPublicDetail';
import JobApplication from './pages/jobs/JobApplication';
import RecruiterRequests from './pages/admin/RecruiterRequests';
import RecruiterRequestDetail from './pages/admin/RecruiterRequestDetail';
import AdminUsers from './pages/admin/Users';
import AdminUserDetail from './pages/admin/UserDetail';
import Profile from './pages/profile/Profile';
import RecruiterRequest from './pages/RecruiterRequest';
import CreateJob from './pages/recruiter/CreateJob';
import MyJobs from './pages/recruiter/MyJobs';
import JobDetail from './pages/recruiter/JobDetail';
import EditJob from './pages/recruiter/EditJob';
import JobApplications from './pages/recruiter/JobApplications';
import ApplicationDetail from './pages/recruiter/ApplicationDetail';
import ApiTest from './pages/ApiTest';
import ProtectedRoute from './components/common/ProtectedRoute';
import RoleRoute from './components/common/RoleRoute';

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Layout><Home /></Layout>} />
              <Route path="/jobs" element={<Layout><Jobs /></Layout>} />
              <Route path="/jobs/:id" element={<Layout><JobPublicDetail /></Layout>} />
              <Route path="/jobs/:id/apply" element={<Layout><ProtectedRoute><JobApplication /></ProtectedRoute></Layout>} />
              <Route path="/login" element={<Layout><Login /></Layout>} />
              <Route path="/register" element={<Layout><Register /></Layout>} />
              <Route path="/verify-email" element={<Layout><VerifyEmail /></Layout>} />
              <Route path="/forgot-password" element={<Layout><ForgotPassword /></Layout>} />
              <Route path="/reset-password" element={<Layout><ResetPassword /></Layout>} />

              
              {/* Protected Routes */}
              <Route path="/profile" element={<Layout><ProtectedRoute><Profile /></ProtectedRoute></Layout>} />
              <Route path="/dashboard/candidate" element={<Layout><ProtectedRoute><RoleRoute role="candidate"><CandidateDashboard /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/candidate/saved-jobs" element={<Layout><ProtectedRoute><RoleRoute role="candidate"><CandidateSavedJobs /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/candidate/applications" element={<Layout><ProtectedRoute><RoleRoute role="candidate"><CandidateApplications /></RoleRoute></ProtectedRoute></Layout>} />

              <Route path="/dashboard/recruiter" element={<Layout><ProtectedRoute><RoleRoute role="recruiter"><RecruiterDashboard /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/recruiter/create-job" element={<Layout><ProtectedRoute><RoleRoute role="recruiter"><CreateJob /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/recruiter/my-jobs" element={<Layout><ProtectedRoute><RoleRoute role="recruiter"><MyJobs /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/recruiter/my-jobs/:id" element={<Layout><ProtectedRoute><RoleRoute role="recruiter"><JobDetail /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/recruiter/jobs/:jobId/applications" element={<Layout><ProtectedRoute><RoleRoute role="recruiter"><JobApplications /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/recruiter/applications/:applicationId" element={<Layout><ProtectedRoute><RoleRoute role="recruiter"><ApplicationDetail /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/recruiter/edit-job/:id" element={<Layout><ProtectedRoute><RoleRoute role="recruiter"><EditJob /></RoleRoute></ProtectedRoute></Layout>} />

              <Route path="/dashboard/admin" element={<Layout><ProtectedRoute><RoleRoute role="admin"><AdminDashboard /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/admin/recruiter-requests" element={<Layout><ProtectedRoute><RoleRoute role="admin"><RecruiterRequests /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/admin/recruiter-requests/:id" element={<Layout><ProtectedRoute><RoleRoute role="admin"><RecruiterRequestDetail /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/admin/users" element={<Layout><ProtectedRoute><RoleRoute role="admin"><AdminUsers /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/admin/users/:id" element={<Layout><ProtectedRoute><RoleRoute role="admin"><AdminUserDetail /></RoleRoute></ProtectedRoute></Layout>} />
              <Route path="/recruiter-request" element={<Layout><ProtectedRoute><RecruiterRequest /></ProtectedRoute></Layout>} />
              
              {/* Debug Route */}
              <Route path="/api-test" element={<Layout><ApiTest /></Layout>} />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;