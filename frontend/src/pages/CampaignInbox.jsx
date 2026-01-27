import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // <--- Added useNavigate
import { api } from '../services/api';

const CampaignInbox = () => {
  const { id } = useParams(); 
  const navigate = useNavigate(); // <--- Initialize hook
  const [data, setData] = useState(null);
  const [selectedLeadId, setSelectedLeadId] = useState(null);
  const [newMessage, setNewMessage] = useState("");
  const [sending, setSending] = useState(false);
  
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchInbox();
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [selectedLeadId, data]);

  const fetchInbox = async () => {
    try {
      const response = await api.getCampaignInbox(id);
      setData(response);
      
      if (!selectedLeadId && response.conversations.length > 0) {
        setSelectedLeadId(response.conversations[0].lead_id);
      }
    } catch (error) {
      console.error("Failed to load inbox", error);
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
      await fetchInbox(); 
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

  if (!data) return <div className="p-10 text-center text-gray-500">Loading inbox...</div>;

  const activeChat = data.conversations.find(c => c.lead_id === selectedLeadId);

  return (
    <div className="flex h-[calc(100vh-64px)] bg-gray-50">
      {/* --- LEFT SIDEBAR --- */}
      <div className="w-1/3 border-r border-gray-200 bg-white flex flex-col">
        {/* Header with Back Button */}
        <div className="p-4 border-b border-gray-100 bg-gray-50">
          <button 
            onClick={() => navigate('/campaigns')}
            className="text-sm text-gray-500 hover:text-blue-600 flex items-center mb-3 transition-colors font-medium"
          >
            <span className="mr-1">←</span> Back to Campaigns
          </button>
          <h2 className="font-bold text-gray-800 text-lg">{data.campaign_name}</h2>
          <p className="text-xs text-gray-500 mt-1">{data.conversations.length} Conversations</p>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {data.conversations.map((conv) => (
            <div 
              key={conv.lead_id}
              onClick={() => setSelectedLeadId(conv.lead_id)}
              className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                selectedLeadId === conv.lead_id ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-semibold text-gray-900 truncate pr-2">
                  {conv.owner_name || "Unknown Lead"}
                </span>
                <span className="text-xs text-gray-400 whitespace-nowrap">
                  {conv.last_activity_at ? new Date(conv.last_activity_at).toLocaleDateString() : ''}
                </span>
              </div>
              <p className="text-sm text-gray-500 truncate">
                {conv.address || conv.phone_number}
              </p>
              <div className="mt-2 flex items-center justify-between">
                <span className={`text-xs px-2 py-0.5 rounded-full inline-block ${
                  conv.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                }`}>
                  {conv.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* --- RIGHT SIDE: CHAT WINDOW --- */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {activeChat ? (
          <>
            {/* Header */}
            <div className="p-4 bg-white border-b border-gray-200 shadow-sm flex justify-between items-center">
              <div>
                <h3 className="font-bold text-gray-800">{activeChat.owner_name || activeChat.lead_id}</h3>
                <p className="text-sm text-gray-500">{activeChat.phone_number} • {activeChat.address}</p>
              </div>
              <div className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">ID: {activeChat.lead_id}</div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {activeChat.messages.length === 0 ? (
                <div className="text-center text-gray-400 mt-10">No messages yet.</div>
              ) : (
                activeChat.messages.map((msg) => {
                  const isOutbound = msg.direction.includes('outbound');
                  return (
                    <div key={msg.id} className={`flex ${isOutbound ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[70%] rounded-2xl px-4 py-2 shadow-sm whitespace-pre-wrap ${
                        isOutbound 
                          ? 'bg-blue-600 text-white rounded-br-none' 
                          : 'bg-white text-gray-800 border border-gray-200 rounded-bl-none'
                      }`}>
                        <p className="text-sm">{msg.body}</p>
                        <div className={`text-[10px] mt-1 text-right ${isOutbound ? 'text-blue-100' : 'text-gray-400'}`}>
                          {new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-200">
              <form onSubmit={handleSendMessage} className="flex gap-2 items-end">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type a message... (Shift+Enter for new line)"
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none h-14 text-sm"
                />
                <button 
                  type="submit" 
                  disabled={sending}
                  className="bg-blue-600 text-white px-6 h-14 rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50 flex items-center justify-center transition-colors"
                >
                  {sending ? '...' : 'Send'}
                </button>
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            Select a conversation to start chatting
          </div>
        )}
      </div>
    </div>
  );
};

export default CampaignInbox;
