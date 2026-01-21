import axios from 'axios';

// 1. Point to your Python Backend
const API_URL = 'http://localhost:9999/api';

// 2. Create a "Client"
const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- NEW: INTERCEPTOR (The Gatekeeper) ---
// Automatically injects the token into every request
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const api = {
  // --- AUTH SERVICES (NEW) ---
  
  // Login: Special handling for FastAPI OAuth2 Form Data
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email); // FastAPI looks for 'username' field
    formData.append('password', password);

    const response = await client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  signup: async (userData) => {
    // userData = { email, password, full_name }
    const response = await client.post('/auth/signup', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await client.get('/auth/me');
    return response.data;
  },

  // --- SEARCH ENDPOINTS ---
  scanArea: async (state, city, strategy) => {
    const response = await client.post('/search/scan', { state, city, strategy });
    return response.data;
  },

  enrichLeads: async (ids, state, city, strategy) => {
    const response = await client.post('/search/enrich', {
      radar_ids: ids,
      state,
      city,
      strategy
    });
    return response.data;
  },

  // --- HISTORY ENDPOINTS ---
  getHistory: async () => {
    const response = await client.get('/history/');
    return response.data;
  },

  getLeads: async (searchId) => {
    const response = await client.get(`/history/${searchId}`);
    return response.data;
  }
};
