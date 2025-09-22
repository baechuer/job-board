import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import VerifyEmail from './pages/auth/VerifyEmail';
import AdminDashboard from './pages/dashboard/AdminDashboard';
import RecruiterDashboard from './pages/dashboard/RecruiterDashboard';
import CandidateDashboard from './pages/dashboard/CandidateDashboard';
import RecruiterRequests from './pages/admin/RecruiterRequests';
import Profile from './pages/profile/Profile';
import RecruiterRequest from './pages/RecruiterRequest';

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
              <Route path="/login" element={<Layout><Login /></Layout>} />
              <Route path="/register" element={<Layout><Register /></Layout>} />
              <Route path="/verify-email" element={<Layout><VerifyEmail /></Layout>} />
              
              {/* Protected Routes */}
              <Route path="/dashboard/admin" element={<Layout><AdminDashboard /></Layout>} />
              <Route path="/dashboard/recruiter" element={<Layout><RecruiterDashboard /></Layout>} />
              <Route path="/dashboard/candidate" element={<Layout><CandidateDashboard /></Layout>} />
              <Route path="/admin/recruiter-requests" element={<Layout><RecruiterRequests /></Layout>} />
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