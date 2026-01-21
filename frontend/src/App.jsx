import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Auth & Security Components
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/layout/ProtectedRoute';

// Layouts
import MainLayout from './components/layout/MainLayout';

// Pages
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Campaigns from './pages/Campaigns';
import Login from './pages/Login';
import Signup from './pages/Signup';

function App() {
  return (
    // 1. Wrap the entire app in AuthProvider so 'useAuth()' works everywhere
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          
          {/* --- PUBLIC ROUTES (No MainLayout, No Protection) --- */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* --- PROTECTED ROUTES (Wrapped in MainLayout) --- */}
          {/* We use a wildcard '/*' so this Route handles all other paths */}
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
