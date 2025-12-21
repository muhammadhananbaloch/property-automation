import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ScanForm } from '../components/features/ScanForm';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button'; 
import { Table } from '../components/ui/Table';
import { CheckCircle2, AlertCircle, ShoppingCart, ArrowRight, Eye, RefreshCw, ArrowLeft, MapPin } from 'lucide-react';

const Dashboard = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [scanResult, setScanResult] = useState(null);
  const [searchCriteria, setSearchCriteria] = useState(null);
  const [purchaseLimit, setPurchaseLimit] = useState(1);
  const [enrichedLeads, setEnrichedLeads] = useState(null);

  // --- VIEW STATE ---
  const [showOwnedList, setShowOwnedList] = useState(false);
  
  // --- SELECTION STATE FOR RE-ENRICHMENT ---
  const [selectedOwnedIds, setSelectedOwnedIds] = useState([]);

  // Reset selection when scan result changes
  useEffect(() => {
    if (scanResult) {
      setPurchaseLimit(Math.min(10, scanResult.new_count));
      setSelectedOwnedIds([]); 
    }
  }, [scanResult]);

  // --- HANDLERS ---
  const handleScan = async (formData) => {
    setIsLoading(true);
    setError(null);
    setScanResult(null);
    setEnrichedLeads(null);
    setSearchCriteria(formData);
    setShowOwnedList(false); // Reset to "New" tab on a fresh scan

    try {
      const data = await api.scanArea(formData.state, formData.city, formData.strategy);
      setScanResult(data);
    } catch (err) {
      console.error(err);
      setError("Failed to connect to scanner.");
    } finally {
      setIsLoading(false);
    }
  };

  // Manual Refresh Button Handler
  const handleRefresh = async () => {
    if (!searchCriteria) return;
    await handleScan(searchCriteria);
  };

  const handleEnrich = async (idsToProcess = null) => {
    if (!scanResult || !searchCriteria) return;
    
    // If no specific IDs passed, use the slider for NEW leads
    const finalIds = idsToProcess || scanResult.leads.map(l => l.id).slice(0, purchaseLimit);
    
    if (finalIds.length === 0) return;

    setIsLoading(true);
    try {
      await api.enrichLeads(
        finalIds, 
        searchCriteria.state, 
        searchCriteria.city, 
        searchCriteria.strategy
      );
      
      const history = await api.getHistory();
      if (history && history.length > 0) {
        const leadsData = await api.getLeads(history[0].id);
        const freshLeads = Array.isArray(leadsData) ? leadsData : leadsData.leads || [];
        setEnrichedLeads(freshLeads);

        // Update Local State Immediately
        setScanResult(prev => {
            if (!prev) return null;

            const freshIds = freshLeads.map(l => l.radar_id);

            // 1. Update Existing Owned (if we re-enriched them)
            const updatedExistingOwned = prev.purchased_leads.map(existing => {
                const match = freshLeads.find(f => f.radar_id === existing.radar_id);
                return match || existing;
            });

            // 2. Identify Newly Purchased (that were previously "New")
            const newlyAdded = freshLeads.filter(f => 
                !prev.purchased_leads.some(p => p.radar_id === f.radar_id)
            );

            // 3. Remove Purchased from "New Leads" List
            const updatedNewLeadsPreview = prev.leads.filter(l => !freshIds.includes(l.id));

            return {
                ...prev,
                new_count: updatedNewLeadsPreview.length,
                leads: updatedNewLeadsPreview,
                purchased_count: updatedExistingOwned.length + newlyAdded.length,
                purchased_leads: [...newlyAdded, ...updatedExistingOwned]
            };
        });
      }
      
      setSelectedOwnedIds([]);

    } catch (err) {
      console.error(err);
      setError("Enrichment failed. Check console.");
    } finally {
      setIsLoading(false);
    }
  };

  // --- TOGGLE LOGIC ---
  const toggleOwnedSelection = (id) => {
    setSelectedOwnedIds(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const selectAllOwned = () => {
    if (selectedOwnedIds.length === (scanResult?.purchased_leads?.length || 0)) {
      setSelectedOwnedIds([]); // Deselect all
    } else {
      setSelectedOwnedIds(scanResult.purchased_leads.map(l => l.radar_id));
    }
  };

  const toggleToNew = () => setShowOwnedList(false);
  const toggleToOwned = () => setShowOwnedList(true);
  
  const handleBackToResults = () => {
      setEnrichedLeads(null);
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto">
      
      {/* HEADER WITH REFRESH BUTTON */}
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500">Manage your property harvesting operations.</p>
        </div>
        {scanResult && !enrichedLeads && (
            <Button variant="outline" onClick={handleRefresh} isLoading={isLoading}>
                <RefreshCw size={16} className="mr-2" /> Refresh Data
            </Button>
        )}
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-center gap-3">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {/* VIEW 1: FORM */}
      {!scanResult && !enrichedLeads && (
        <ScanForm onScan={handleScan} isLoading={isLoading} />
      )}

      {/* VIEW 2: SCAN RESULT */}
      {scanResult && !enrichedLeads && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* --- NEW: CRITERIA CONTEXT HEADER --- */}
          <div className="flex items-center gap-2 text-slate-500 pb-2 border-b border-slate-100">
             <MapPin size={18} className="text-brand-500" />
             <span className="text-lg">
                Results for <strong className="text-slate-900">{searchCriteria?.city}, {searchCriteria?.state}</strong>
             </span>
             <span className="text-slate-300 mx-2">|</span>
             <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs font-bold uppercase tracking-wider">
                {searchCriteria?.strategy?.replace(/_/g, ' ')}
             </span>
          </div>

          {/* STATS CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-6 border-l-4 border-l-green-500 bg-green-50/30 flex items-center gap-4">
               <div className="p-3 bg-green-100 rounded-full text-green-600">
                 <CheckCircle2 size={24} />
               </div>
               <div>
                 <p className="text-sm font-bold text-slate-500 uppercase">Status</p>
                 <p className="text-lg font-bold text-slate-900">Scout Complete</p>
               </div>
            </Card>

            <div onClick={toggleToNew} className="cursor-pointer group">
              <Card className={`p-6 border-l-4 border-l-brand-500 transition-all duration-200 ${!showOwnedList ? 'bg-white ring-2 ring-brand-200 shadow-md transform scale-[1.02]' : 'bg-white hover:bg-slate-50 opacity-70'}`}>
                <p className="text-sm font-bold text-slate-500 uppercase">New Leads</p>
                <p className="text-3xl font-bold text-brand-600 mt-1">{scanResult.new_count}</p>
                <p className="text-xs text-slate-400 mt-1">Available to Buy</p>
              </Card>
            </div>

            <div onClick={toggleToOwned} className="cursor-pointer group">
              <Card className={`p-6 border-l-4 border-l-slate-300 transition-all duration-200 ${showOwnedList ? 'bg-white ring-2 ring-slate-400 shadow-md transform scale-[1.02]' : 'bg-slate-50 hover:bg-white'}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-bold text-slate-400 uppercase">Already Owned</p>
                    <p className="text-3xl font-bold text-slate-600 mt-1">{scanResult.purchased_count}</p>
                    <p className="text-xs text-slate-400 mt-1">Ready to Update</p>
                  </div>
                  <div className={`p-2 rounded-full transition-colors ${showOwnedList ? 'bg-slate-800 text-white' : 'bg-slate-200 text-slate-400 group-hover:bg-slate-300'}`}>
                     <RefreshCw size={18} />
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* DYNAMIC CONTENT AREA */}
          {showOwnedList ? (
            /* VIEW A: ALREADY OWNED TABLE (With Re-Enrichment) */
            <Card className="p-6 bg-slate-50 border-2 border-slate-200 animate-in fade-in zoom-in-95 duration-200">
               <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-4">
                      <h3 className="font-bold text-slate-700 flex items-center gap-2">
                        <CheckCircle2 size={20} className="text-green-600"/> 
                        Existing Leads
                      </h3>
                      {selectedOwnedIds.length > 0 && (
                          <span className="text-xs bg-brand-100 text-brand-700 px-2 py-1 rounded-full font-bold">
                              {selectedOwnedIds.length} Selected
                          </span>
                      )}
                  </div>
                  
                  <div className="flex gap-3">
                      <Button variant="outline" size="sm" onClick={toggleToNew}>
                        Cancel
                      </Button>
                      <Button 
                        size="sm" 
                        disabled={selectedOwnedIds.length === 0}
                        onClick={() => handleEnrich(selectedOwnedIds)}
                        isLoading={isLoading}
                      >
                        <RefreshCw size={16} className="mr-2" />
                        Update Selected
                      </Button>
                  </div>
               </div>
               
               <div className="bg-white rounded-lg border border-slate-200 overflow-hidden overflow-x-auto">
                 <table className="w-full text-left text-sm text-slate-600">
                    <thead className="bg-slate-50 border-b border-slate-200 font-bold text-slate-700 uppercase text-xs">
                        <tr>
                            <th className="px-6 py-4 w-10">
                                <input 
                                    type="checkbox" 
                                    onChange={selectAllOwned}
                                    checked={selectedOwnedIds.length === scanResult.purchased_leads.length && scanResult.purchased_leads.length > 0}
                                    className="rounded border-slate-300 text-brand-600 focus:ring-brand-500"
                                />
                            </th>
                            {["Address", "City", "Owner", "Equity", "Value", "Beds", "Baths", "SqFt", "Year", "Phone", "Email", "Status"].map(h => (
                                <th key={h} className="px-6 py-4">{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {(scanResult.purchased_leads || []).map((lead, i) => (
                          <tr key={i} className={`hover:bg-slate-50 transition-colors ${selectedOwnedIds.includes(lead.radar_id) ? 'bg-brand-50/30' : ''}`}>
                            <td className="px-6 py-4">
                                <input 
                                    type="checkbox" 
                                    checked={selectedOwnedIds.includes(lead.radar_id)}
                                    onChange={() => toggleOwnedSelection(lead.radar_id)}
                                    className="rounded border-slate-300 text-brand-600 focus:ring-brand-500"
                                />
                            </td>
                            <td className="px-6 py-4 font-medium text-slate-900">{lead.address}</td>
                            <td className="px-6 py-4 text-slate-600">{lead.city}</td>
                            
                            {/* WRAPPED OWNER NAME */}
                            <td className="px-6 py-4 text-slate-800 font-medium whitespace-normal break-words max-w-[180px]">
                                {lead.owner_name}
                            </td>

                            <td className="px-6 py-4 text-green-700 font-bold">${(lead.equity_value || 0).toLocaleString()}</td>
                            <td className="px-6 py-4 text-slate-600">${(lead.estimated_value || 0).toLocaleString()}</td>
                            <td className="px-6 py-4 text-slate-600">{lead.beds}</td>
                            <td className="px-6 py-4 text-slate-600">{lead.baths}</td>
                            <td className="px-6 py-4 text-slate-600 font-medium">{lead.sq_ft ? lead.sq_ft.toLocaleString() : '-'}</td>
                            <td className="px-6 py-4 text-slate-600">{lead.year_built}</td>
                            
                            <td className="px-6 py-4">
                                <div className="flex flex-col gap-1">
                                    {lead.phone_numbers && lead.phone_numbers.map((p, idx) => (
                                        <span key={idx} className="text-xs font-mono text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded w-fit">{p}</span>
                                    ))}
                                    {!lead.phone_numbers?.length && <span className="text-slate-300 text-xs">-</span>}
                                </div>
                            </td>
                            
                            <td className="px-6 py-4">
                                <div className="flex flex-col gap-1">
                                    {lead.emails && lead.emails.map((e, idx) => (
                                        <span key={idx} className="text-xs text-slate-500 truncate max-w-[100px]" title={e}>{e}</span>
                                    ))}
                                    {!lead.emails?.length && <span className="text-slate-300 text-xs">-</span>}
                                </div>
                            </td>

                            <td className="px-6 py-4">
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Owned</span>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                 </table>
                 {(scanResult.purchased_leads || []).length === 0 && (
                     <div className="p-8 text-center text-slate-400">No owned leads details found.</div>
                 )}
               </div>
            </Card>
          ) : (
            /* VIEW B: PURCHASE SLIDER (Default) */
            <Card className="p-8 border-dashed border-2 border-slate-300 bg-slate-50 animate-in fade-in zoom-in-95 duration-200">
              <div className="max-w-xl mx-auto text-center">
                <h3 className="text-lg font-bold text-slate-900 mb-2">How many new leads do you want?</h3>
                <p className="text-slate-500 mb-6">Use the slider to choose how many credits to spend.</p>
                
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm mb-8">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-sm font-medium text-slate-500">Quantity</span>
                    <span className="text-2xl font-bold text-brand-600">{purchaseLimit} Leads</span>
                  </div>
                  <input 
                    type="range" 
                    min="1" 
                    max={scanResult.new_count || 1} 
                    value={purchaseLimit}
                    onChange={(e) => setPurchaseLimit(parseInt(e.target.value))}
                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
                  />
                  <div className="flex justify-between text-xs text-slate-400 mt-2">
                    <span>1</span>
                    <span>{scanResult.new_count} (Max)</span>
                  </div>
                </div>
                
                <div className="flex justify-center gap-4">
                  <button onClick={() => setScanResult(null)} className="px-4 py-2 text-slate-600 font-medium hover:text-slate-900">
                    Cancel
                  </button>
                  <Button onClick={() => handleEnrich(null)} isLoading={isLoading}>
                    <ShoppingCart size={18} />
                    Buy {purchaseLimit} Leads
                  </Button>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* VIEW 3: SUCCESS RESULT */}
      {enrichedLeads && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-brand-100 text-brand-700 rounded-lg"><CheckCircle2 size={24} /></div>
              <div><h2 className="text-xl font-bold text-slate-900">Success! Leads processed.</h2></div>
            </div>
            
            <div className="flex gap-3">
                <Button variant="outline" onClick={handleBackToResults}>
                  <ArrowLeft size={16} className="mr-2" /> Back to Results
                </Button>
                
                <Button variant="default" onClick={() => { setEnrichedLeads(null); setScanResult(null); }}>
                  Start New Scan <ArrowRight size={16} className="ml-2" />
                </Button>
            </div>
          </div>
          
           <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden overflow-x-auto">
            <Table headers={["Address", "City", "Owner", "Equity", "Value", "Beds", "Baths", "SqFt", "Year", "Phone", "Email"]}>
              {enrichedLeads.map((lead, index) => (
                <tr key={index} className="hover:bg-slate-50 transition-colors border-b border-slate-100">
                  <td className="px-6 py-4 font-medium text-slate-900">{lead.address || "N/A"}</td>
                  <td className="px-6 py-4 text-slate-600">{lead.city}</td>
                  
                  {/* WRAPPED OWNER NAME */}
                  <td className="px-6 py-4 text-slate-800 font-medium whitespace-normal break-words max-w-[180px]">
                      {lead.owner_name}
                  </td>

                  <td className="px-6 py-4 font-bold text-green-700">${(lead.equity_value || 0).toLocaleString()}</td>
                  <td className="px-6 py-4 text-slate-600">${(lead.estimated_value || 0).toLocaleString()}</td>
                  <td className="px-6 py-4 text-slate-600">{lead.beds}</td>
                  <td className="px-6 py-4 text-slate-600">{lead.baths}</td>
                  <td className="px-6 py-4 text-slate-600 font-medium">{lead.sq_ft ? lead.sq_ft.toLocaleString() : '-'}</td>
                  <td className="px-6 py-4 text-slate-600">{lead.year_built}</td>
                  <td className="px-6 py-4">
                     <div className="flex flex-col gap-1">
                        {lead.phone_numbers && lead.phone_numbers.map((p, idx) => (
                            <span key={`p-${idx}`} className="text-xs font-mono text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded w-fit">{p}</span>
                        ))}
                        {!lead.phone_numbers?.length && <span className="text-slate-300 text-xs">-</span>}
                     </div>
                  </td>
                  <td className="px-6 py-4">
                     <div className="flex flex-col gap-1">
                        {lead.emails && lead.emails.map((e, idx) => (
                            <span key={`e-${idx}`} className="text-xs text-slate-500 truncate max-w-[150px]" title={e}>{e}</span>
                        ))}
                        {!lead.emails?.length && <span className="text-slate-300 text-xs">-</span>}
                     </div>
                  </td>
                </tr>
              ))}
            </Table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
