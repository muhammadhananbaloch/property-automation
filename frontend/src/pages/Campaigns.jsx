import React, { useEffect, useState } from 'react';
import { api } from '../services/api'; 
import { useNavigate } from 'react-router-dom';

const Campaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const data = await api.getCampaigns();
      setCampaigns(data);
    } catch (error) {
      console.error("Failed to load campaigns", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-gray-500 mt-1">Manage your SMS blasts and conversations</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium shadow-sm transition-colors opacity-50 cursor-not-allowed" title="Start campaigns from the Leads page">
          + New Campaign
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
           <div className="text-gray-500 animate-pulse">Loading campaigns...</div>
        </div>
      ) : campaigns.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="text-gray-400 mb-2">📭</div>
          <h3 className="text-lg font-medium text-gray-900">No campaigns yet</h3>
          <p className="text-gray-500 mt-1">Start your first SMS blast from the Leads page.</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((campaign) => (
            <div 
              key={campaign.id} 
              onClick={() => navigate(`/campaigns/${campaign.id}`)}
              className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer p-6 group"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="h-10 w-10 bg-blue-50 rounded-full flex items-center justify-center text-blue-600 font-bold text-lg group-hover:bg-blue-100 transition-colors">
                  {campaign.name.charAt(0).toUpperCase()}
                </div>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium uppercase tracking-wide ${getStatusColor(campaign.status)}`}>
                  {campaign.status}
                </span>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2 truncate" title={campaign.name}>
                {campaign.name}
              </h3>
              
              <div className="space-y-3 pt-4 border-t border-gray-100">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Total Leads</span>
                  <span className="font-medium text-gray-900">{campaign.total_leads}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Created</span>
                  <span className="text-gray-900">{new Date(campaign.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Campaigns;
