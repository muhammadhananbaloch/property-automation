import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../../services/api';
import { X, MessageSquare, Send, AlertTriangle } from 'lucide-react';

const CreateCampaignModal = ({ selectedLeads, defaultName, onClose, onSuccess }) => {
  const [name, setName] = useState('');
  const [template, setTemplate] = useState("Hi {name}, I saw your property at {address}. Are you interested in selling?");
  const [loading, setLoading] = useState(false);

  // --- SMART FILTERING ---
  // We separate leads into "Valid" (has phone) and "Invalid" (no phone)
  const { validLeads, invalidCount } = useMemo(() => {
    const valid = selectedLeads.filter(l => l.phone_numbers && l.phone_numbers.length > 0);
    return {
      validLeads: valid,
      invalidCount: selectedLeads.length - valid.length
    };
  }, [selectedLeads]);

  useEffect(() => {
    if (defaultName) setName(defaultName);
  }, [defaultName]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !template) return;
    if (validLeads.length === 0) return; // Prevention

    setLoading(true);
    try {
      // ONLY send the IDs of leads that actually have phones
      const leadIds = validLeads.map(l => l.radar_id);
      
      await api.startCampaign({
        name: name,
        template_body: template,
        lead_ids: leadIds
      });
      
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Failed to start campaign", error);
      alert("Failed to start campaign. Check console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden border border-slate-200">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <div className="flex items-center gap-2 text-slate-800">
            <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
              <MessageSquare size={18} />
            </div>
            <h3 className="font-bold text-lg">Launch SMS Campaign</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          
          {/* STATUS BANNER */}
          <div>
            {validLeads.length > 0 ? (
              <div className="bg-blue-50 text-blue-800 px-4 py-3 rounded-lg text-sm flex flex-col gap-1 border border-blue-100">
                <div className="flex items-center">
                  <span className="mr-2">🎯</span>
                  Targeting <strong className="mx-1">{validLeads.length}</strong> valid leads
                </div>
                {invalidCount > 0 && (
                  <div className="text-xs text-blue-600/80 pl-6">
                    (Skipped {invalidCount} leads without phone numbers)
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-red-50 text-red-800 px-4 py-3 rounded-lg text-sm flex items-center gap-2 border border-red-100">
                <AlertTriangle size={16} />
                <span>None of the selected leads have phone numbers!</span>
              </div>
            )}
          </div>

          {/* INPUTS */}
          <div className={validLeads.length === 0 ? 'opacity-50 pointer-events-none' : ''}>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1.5">Campaign Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                placeholder="e.g. Richmond Blast"
                required
              />
            </div>

            <div className="mt-4">
              <label className="block text-sm font-bold text-slate-700 mb-1.5">Message Template</label>
              <textarea
                value={template}
                onChange={(e) => setTemplate(e.target.value)}
                rows="4"
                className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none transition-all"
                required
              />
              <p className="text-xs text-slate-500 mt-1.5">
                Variables: <code className="bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200 text-slate-600 font-mono">{`{name}`}</code>, <code className="bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200 text-slate-600 font-mono">{`{address}`}</code>
              </p>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="pt-2 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium text-sm transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || validLeads.length === 0}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-bold text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm shadow-blue-200"
            >
              {loading ? 'Launching...' : <><Send size={16} /> Launch Campaign</>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCampaignModal;
