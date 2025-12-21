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

export const api = {
  // --- SEARCH ENDPOINTS ---
  
  // The Scout: Scans an area for new leads
  scanArea: async (state, city, strategy) => {
    const response = await client.post('/search/scan', { state, city, strategy });
    return response.data;
  },

  // The Buyer: Enriches specific leads
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

  // Get list of past searches
  getHistory: async () => {
    const response = await client.get('/history/');
    return response.data;
  },

  // Get the leads inside a specific search
  getLeads: async (searchId) => {
    const response = await client.get(`/history/${searchId}`);
    return response.data;
  }
};
