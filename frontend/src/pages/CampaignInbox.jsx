import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Send, RefreshCw, User, Phone, MapPin, ArrowLeft } from 'lucide-react';

const CampaignInbox = () => {
  const { id } = useParams(); 
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [selectedLeadId, setSelectedLeadId] = useState(null);
  const [newMessage, setNewMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  
  const chatEndRef = useRef(null);

  // 1. Initial Fetch & Polling Setup
  useEffect(() => {
    fetchInbox();
    
    // Poll every 5 seconds to check for new replies
    const interval = setInterval(() => {
      setIsPolling(true);
      fetchInbox(true); // true = silent background refresh
    }, 5000);

    return () => clearInterval(interval);
  }, [id]);

  // 2. Scroll to bottom when switching chats or getting new messages
  useEffect(() => {
    scrollToBottom();
  }, [selectedLeadId, data]);

  const fetchInbox = async (isBackground = false) => {
    try {
      const response = await api.getCampaignInbox(id);
      setData(response);
      
      // Select first lead on initial load
      if (!selectedLeadId && response.conversations.length > 0) {
        setSelectedLeadId(response.conversations[0].lead_id);
      }
    } catch (error) {
      console.error("Failed to load inbox", error);
    } finally {
      if (isBackground) setIsPolling(false);
    }
  };

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault(); 
    if (!newMessage.trim()) return;

    setSending(true);
    try {
      await api.sendOneOffMessage({
        lead_id: selectedLeadId,
        body: newMessage,
        campaign_id: parseInt(id)
      });
      
      setNewMessage("");
      await fetchInbox(); // Instant refresh after sending
    } catch (error) {
      alert("Failed to send message");
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); 
      handleSendMessage(e); 
    }
  };

  // Helper for Status Badges
  const getStatusBadge = (status) => {
    switch (status) {
      case 'replied': return 'bg-purple-100 text-purple-700 border-purple-200 font-bold'; // The "Gold" status
      case 'sent': return 'bg-green-100 text-green-700 border-green-200';
      case 'queued': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'failed': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  if (!data) return (
    <div className="flex h-screen items-center justify-center bg-gray-50">
      <div className="text-gray-400 animate-pulse flex items-center gap-2">
        <RefreshCw className="animate-spin" size={20}/> Loading conversations...
      </div>
    </div>
  );

  const activeChat = data.conversations.find(c => c.lead_id === selectedLeadId);

  return (
    <div className="flex h-[calc(100vh-64px)] bg-white border-t border-gray-200">
      
      {/* --- LEFT SIDEBAR (Lead List) --- */}
      <div className="w-1/3 min-w-[320px] border-r border-gray-200 flex flex-col bg-slate-50">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 bg-white shadow-sm z-10">
          <button 
            onClick={() => navigate('/campaigns')}
            className="text-xs text-slate-500 hover:text-blue-600 flex items-center mb-3 transition-colors font-semibold uppercase tracking-wider"
          >
            <ArrowLeft size={14} className="mr-1" /> Back to Campaigns
          </button>
          <div className="flex justify-between items-end">
            <div>
              <h2 className="font-bold text-slate-900 text-lg truncate w-64" title={data.campaign_name}>{data.campaign_name}</h2>
              <p className="text-xs text-slate-500 mt-1">{data.conversations.length} Leads</p>
            </div>
            {isPolling && <RefreshCw size={14} className="text-blue-400 animate-spin" title="Syncing..." />}
          </div>
        </div>
        
        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {data.conversations.length === 0 ? (
             <div className="p-8 text-center text-gray-400 text-sm">No conversations yet.</div>
          ) : (
            data.conversations.map((conv) => (
              <div 
                key={conv.lead_id}
                onClick={() => setSelectedLeadId(conv.lead_id)}
                className={`p-4 border-b border-gray-100 cursor-pointer transition-all hover:bg-white ${
                  selectedLeadId === conv.lead_id ? 'bg-white border-l-4 border-l-blue-600 shadow-md' : 'bg-slate-50/50 border-l-4 border-l-transparent'
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className={`font-semibold truncate pr-2 ${selectedLeadId === conv.lead_id ? 'text-blue-900' : 'text-slate-700'}`}>
                    {conv.owner_name || "Unknown Lead"}
                  </span>
                  {/* Status Badge */}
                  <span className={`text-[10px] uppercase px-2 py-0.5 rounded-full border ${getStatusBadge(conv.status)}`}>
                    {conv.status}
                  </span>
                </div>
                <p className="text-xs text-slate-500 truncate mb-2">
                  {conv.address || conv.phone_number}
                </p>
                <div className="flex justify-between items-center text-[10px] text-slate-400">
                   <span>ID: {conv.lead_id.substring(0,8)}...</span>
                   <span>{conv.last_activity_at ? new Date(conv.last_activity_at).toLocaleDateString() : ''}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* --- RIGHT SIDE: CHAT WINDOW --- */}
      <div className="flex-1 flex flex-col bg-white">
        {activeChat ? (
          <>
            {/* Chat Header */}
            <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-bold text-slate-900 text-xl">{activeChat.owner_name || activeChat.lead_id}</h3>
                  <span className={`text-[10px] uppercase px-2 py-0.5 rounded-full border ${getStatusBadge(activeChat.status)}`}>{activeChat.status}</span>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-500">
                   <span className="flex items-center gap-1"><Phone size={12}/> {activeChat.phone_number}</span>
                   <span className="flex items-center gap-1"><MapPin size={12}/> {activeChat.address}</span>
                </div>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30">
              {activeChat.messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 opacity-50">
                   <User size={48} className="mb-2" />
                   <p>Start the conversation</p>
                </div>
              ) : (
                activeChat.messages.map((msg) => {
                  const isOutbound = msg.direction.includes('outbound');
                  return (
                    <div key={msg.id} className={`flex w-full ${isOutbound ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[65%] flex flex-col ${isOutbound ? 'items-end' : 'items-start'}`}>
                        {/* Bubble */}
                        <div className={`px-5 py-3 rounded-2xl shadow-sm text-sm whitespace-pre-wrap leading-relaxed ${
                          isOutbound 
                            ? 'bg-blue-600 text-white rounded-br-none' 
                            : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none'
                        }`}>
                          {msg.body}
                        </div>
                        {/* Meta */}
                        <span className="text-[10px] text-slate-400 mt-1 px-1">
                          {isOutbound ? 'You' : activeChat.owner_name} • {new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-100">
              <form onSubmit={handleSendMessage} className="flex gap-3 items-end max-w-4xl mx-auto">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type a message... (Shift+Enter for new line)"
                  className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 resize-none h-14 text-sm transition-all"
                />
                <button 
                  type="submit" 
                  disabled={sending || !newMessage.trim()}
                  className="bg-blue-600 text-white w-14 h-14 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 flex items-center justify-center transition-all shadow-sm hover:shadow-md active:scale-95"
                >
                  {sending ? <RefreshCw className="animate-spin" size={20} /> : <Send size={20} className="ml-0.5" />}
                </button>
              </form>
              <div className="text-center mt-2">
                 <p className="text-[10px] text-slate-300">Press Enter to send</p>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-300">
            <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                <User size={40} />
            </div>
            <p className="font-medium">Select a conversation to start chatting</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CampaignInbox;