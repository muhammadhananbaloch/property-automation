import React, { createContext, useState, useEffect, useContext } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 1. Check for existing session on load
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // Verify token validity by fetching user profile
          const userData = await api.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error("Session expired", error);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  // 2. Login Action
  const login = async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem('token', data.access_token);
    
    // Immediately fetch profile to update UI
    const userData = await api.getCurrentUser();
    setUser(userData);
  };

  // 3. Signup Action
  const signup = async (email, password, fullName) => {
    await api.signup({ email, password, full_name: fullName });
    // Auto-login after signup for better UX
    await login(email, password);
  };

  // 4. Logout Action
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Custom Hook for easy access
export const useAuth = () => useContext(AuthContext);
