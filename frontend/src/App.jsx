import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Auth & Security Components
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/layout/ProtectedRoute';
import PublicRoute from './components/layout/PublicRoute'; // <--- NEW IMPORT

// Layouts
import MainLayout from './components/layout/MainLayout';

// Pages
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Campaigns from './pages/Campaigns';
import Login from './pages/Login';
import Signup from './pages/Signup';
import CampaignInbox from './pages/CampaignInbox';

function App() {
  return (
    // 1. Wrap the entire app in AuthProvider so 'useAuth()' works everywhere
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          
          {/* --- PUBLIC ROUTES (Guest Only) --- */}
          {/* If you are logged in, these will now redirect you to /dashboard */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            } 
          />
          <Route 
            path="/signup" 
            element={
              <PublicRoute>
                <Signup />
              </PublicRoute>
            } 
          />

          {/* --- PROTECTED ROUTES (Wrapped in MainLayout) --- */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Routes>
                    {/* Default redirect to dashboard */}
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    
                    <Route path="dashboard" element={<Dashboard />} />
                    <Route path="history" element={<History />} />
                    <Route path="campaigns" element={<Campaigns />} />
                    <Route path="campaigns/:id" element={<CampaignInbox />} />
                    
                    {/* Catch-all inside protected area */}
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </MainLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
