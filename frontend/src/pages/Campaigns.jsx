import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Archive, ArchiveRestore, Layers, Box, Folder } from 'lucide-react';

const Campaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('active'); // 'active' or 'archived'
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

  const handleToggleArchive = async (e, id) => {
    e.stopPropagation(); // Stop click from opening the campaign
    
    // 1. Optimistic UI Update (Instant feel)
    const campaign = campaigns.find(c => c.id === id);
    const newStatus = campaign.status === 'archived' ? 'completed' : 'archived';
    
    setCampaigns(prev => prev.map(c => 
      c.id === id ? { ...c, status: newStatus } : c
    ));

    // 2. Background API Call
    try {
      await api.archiveCampaign(id);
    } catch (error) {
      console.error("Archive failed", error);
      fetchCampaigns(); // Revert if failed
    }
  };

  const getStatusColor = (status) => {
    if (status === 'processing') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (status === 'archived') return 'bg-gray-100 text-gray-500 border-gray-200';
    return 'bg-green-100 text-green-800 border-green-200';
  };

  // --- FILTERING & GROUPING LOGIC ---
  const activeCampaigns = campaigns.filter(c => c.status !== 'archived');
  const archivedCampaigns = campaigns.filter(c => c.status === 'archived');

  // Helper to group campaigns by "City" (Folder logic)
  const groupCampaigns = (list) => {
    const groups = {};
    list.forEach(c => {
      // Extract group name from campaign name (e.g., "Richmond, VA - Blast 1" -> "Richmond, VA")
      // If name doesn't match pattern, put in "Misc"
      const parts = c.name.split('-');
      const groupName = parts.length > 1 ? parts[0].trim() : 'Miscellaneous';
      
      if (!groups[groupName]) groups[groupName] = [];
      groups[groupName].push(c);
    });
    return groups;
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto">
      
      {/* HEADER & TABS */}
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Campaigns</h1>
          <p className="text-slate-500 mt-1">Manage your SMS blasts and conversations</p>
        </div>
        
        <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200">
          <button
            onClick={() => setActiveTab('active')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'active' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <Layers size={16} /> Active ({activeCampaigns.length})
          </button>
          <button
            onClick={() => setActiveTab('archived')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'archived' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <Box size={16} /> Archived ({archivedCampaigns.length})
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64 text-slate-400 animate-pulse">Loading...</div>
      ) : (
        <>
          {/* --- ACTIVE VIEW (Grid) --- */}
          {activeTab === 'active' && (
             <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 animate-in fade-in">
               {activeCampaigns.length === 0 ? (
                 <div className="col-span-full text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
                    <p className="text-slate-500">No active campaigns. Start one from Dashboard!</p>
                 </div>
               ) : (
                 activeCampaigns.map(campaign => (
                   <CampaignCard 
                      key={campaign.id} 
                      campaign={campaign} 
                      navigate={navigate} 
                      onToggle={handleToggleArchive} 
                      getStatusColor={getStatusColor} 
                   />
                 ))
               )}
             </div>
          )}

          {/* --- ARCHIVED VIEW (Grouped Folders) --- */}
          {activeTab === 'archived' && (
            <div className="space-y-8 animate-in fade-in">
              {archivedCampaigns.length === 0 ? (
                 <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
                    <p className="text-slate-500">Archive is empty.</p>
                 </div>
              ) : (
                Object.entries(groupCampaigns(archivedCampaigns)).map(([groupName, items]) => (
                  <div key={groupName} className="bg-slate-50/50 rounded-xl border border-slate-200 p-6">
                    <h3 className="flex items-center gap-2 font-bold text-slate-700 mb-4">
                      <Folder size={20} className="text-blue-400" /> {groupName} 
                      <span className="text-xs font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{items.length}</span>
                    </h3>
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {items.map(campaign => (
                        <CampaignCard 
                          key={campaign.id} 
                          campaign={campaign} 
                          navigate={navigate} 
                          onToggle={handleToggleArchive} 
                          getStatusColor={getStatusColor} 
                        />
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

// Sub-component for cleaner code
const CampaignCard = ({ campaign, navigate, onToggle, getStatusColor }) => (
  <div 
    onClick={() => navigate(`/campaigns/${campaign.id}`)}
    className={`bg-white rounded-xl border shadow-sm hover:shadow-md transition-all cursor-pointer p-6 group relative ${
      campaign.status === 'archived' ? 'border-slate-100 opacity-80 hover:opacity-100' : 'border-slate-200 hover:border-blue-300'
    }`}
  >
    <div className="flex justify-between items-start mb-4">
      <div className={`h-10 w-10 rounded-full flex items-center justify-center font-bold transition-colors ${
          campaign.status === 'archived' ? 'bg-gray-100 text-gray-500' : 'bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white'
      }`}>
        {campaign.name.charAt(0).toUpperCase()}
      </div>
      <div className="flex items-center gap-2">
         <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${getStatusColor(campaign.status)}`}>
            {campaign.status}
         </span>
         <button 
            onClick={(e) => onToggle(e, campaign.id)}
            className="text-slate-300 hover:text-blue-600 p-1 rounded hover:bg-slate-100 transition-colors"
            title={campaign.status === 'archived' ? "Restore" : "Archive"}
         >
            {campaign.status === 'archived' ? <ArchiveRestore size={16} /> : <Archive size={16} />}
         </button>
      </div>
    </div>
    <h3 className="font-bold text-slate-900 mb-1 truncate">{campaign.name}</h3>
    <div className="flex justify-between text-xs text-slate-500 mt-4 pt-4 border-t border-slate-50">
      <span>{campaign.total_leads} Leads</span>
      <span>{new Date(campaign.created_at).toLocaleDateString()}</span>
    </div>
  </div>
);

export default Campaigns;