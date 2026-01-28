import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="p-10 text-center">Loading...</div>; 
  }

  // THE GUARD: If user is logged in, kick them to dashboard
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  // If user is NOT logged in, let them see the page (Login/Signup)
  return children;
};

export default PublicRoute;
