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
import Jobs from './pages/Jobs';
import JobPublicDetail from './pages/JobPublicDetail';
import RecruiterRequests from './pages/admin/RecruiterRequests';
import RecruiterRequestDetail from './pages/admin/RecruiterRequestDetail';
import Profile from './pages/profile/Profile';
import RecruiterRequest from './pages/RecruiterRequest';
import CreateJob from './pages/recruiter/CreateJob';
import MyJobs from './pages/recruiter/MyJobs';
import JobDetail from './pages/recruiter/JobDetail';
import EditJob from './pages/recruiter/EditJob';

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
              <Route path="/login" element={<Layout><Login /></Layout>} />
              <Route path="/register" element={<Layout><Register /></Layout>} />
              <Route path="/verify-email" element={<Layout><VerifyEmail /></Layout>} />
              <Route path="/forgot-password" element={<Layout><ForgotPassword /></Layout>} />
              <Route path="/reset-password" element={<Layout><ResetPassword /></Layout>} />

              
              {/* Protected Routes */}
              <Route path="/dashboard/admin" element={<Layout><AdminDashboard /></Layout>} />
              <Route path="/dashboard/recruiter" element={<Layout><RecruiterDashboard /></Layout>} />
              <Route path="/recruiter/create-job" element={<Layout><CreateJob /></Layout>} />
              <Route path="/recruiter/my-jobs" element={<Layout><MyJobs /></Layout>} />
              <Route path="/recruiter/my-jobs/:id" element={<Layout><JobDetail /></Layout>} />
              <Route path="/recruiter/edit-job/:id" element={<Layout><EditJob /></Layout>} />
              <Route path="/dashboard/candidate" element={<Layout><CandidateDashboard /></Layout>} />
              <Route path="/admin/recruiter-requests" element={<Layout><RecruiterRequests /></Layout>} />
              <Route path="/admin/recruiter-requests/:id" element={<Layout><RecruiterRequestDetail /></Layout>} />
              <Route path="/profile" element={<Layout><Profile /></Layout>} />
              <Route path="/recruiter-request" element={<Layout><RecruiterRequest /></Layout>} />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;