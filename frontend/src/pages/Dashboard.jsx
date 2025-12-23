import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ScanForm } from '../components/features/ScanForm';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button'; 
import { Table } from '../components/ui/Table';
import { CheckCircle2, AlertCircle, ShoppingCart, ArrowRight, Eye, RefreshCw, ArrowLeft, MapPin, Download } from 'lucide-react';

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
    setShowOwnedList(false);

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

  // --- EXPORT TO CSV HANDLER ---
  const handleExport = () => {
    if (selectedOwnedIds.length === 0) {
        setError("No leads selected. Please check the boxes next to the leads you want to export.");
        setTimeout(() => setError(null), 3000);
        return;
    }

    const leadsToExport = scanResult.purchased_leads.filter(lead => 
        selectedOwnedIds.includes(lead.radar_id)
    );

    if (leadsToExport.length === 0) return;

    const headers = ["Address", "City", "State", "Owner", "Equity", "Value", "Beds", "Baths", "SqFt", "Year Built", "Phone Numbers", "Emails"];
    
    const rows = leadsToExport.map(lead => [
        `"${lead.address || ''}"`,
        `"${lead.city || ''}"`,
        `"${lead.state || ''}"`,
        `"${lead.owner_name || ''}"`,
        lead.equity_value || 0,
        lead.estimated_value || 0,
        lead.beds || 0,
        lead.baths || 0,
        lead.sq_ft || 0,
        lead.year_built || 0,
        `"${(lead.phone_numbers || []).join('; ')}"`, 
        `"${(lead.emails || []).join('; ')}"`         
    ]);

    const csvContent = [
        headers.join(","),
        ...rows.map(e => e.join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `propauto_export_${searchCriteria?.city}_${selectedOwnedIds.length}_leads.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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

  const toggleToNew = () => {
      setShowOwnedList(false);
      setEnrichedLeads(null);
  };
  const toggleToOwned = () => {
      setShowOwnedList(true);
      setEnrichedLeads(null);
  };
  
  const handleBackToResults = () => {
      setEnrichedLeads(null);
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto">
      
      {/* HEADER */}
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500">Manage your property harvesting operations.</p>
        </div>
        {scanResult && (
            <Button variant="outline" onClick={handleRefresh} isLoading={isLoading}>
                <RefreshCw size={16} className="mr-2" /> Refresh Data
            </Button>
        )}
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {/* VIEW 1: FORM */}
      {!scanResult && !enrichedLeads && (
        <ScanForm onScan={handleScan} isLoading={isLoading} />
      )}

      {/* VIEW 2: RESULTS DASHBOARD */}
      {scanResult && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* CONTEXT HEADER */}
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

          {/* INTERACTIVE TABS (STATS CARDS) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* STATUS CARD (Static) */}
            <Card className="p-6 border-l-4 border-l-green-500 bg-green-50/30 flex items-center gap-4">
               <div className="p-3 bg-green-100 rounded-full text-green-600">
                 <CheckCircle2 size={24} />
               </div>
               <div>
                 <p className="text-sm font-bold text-slate-500 uppercase">Status</p>
                 <p className="text-lg font-bold text-slate-900">Scout Complete</p>
               </div>
            </Card>

            {/* TAB: NEW LEADS */}
            <div onClick={toggleToNew} className="group h-full">
              <Card className={`p-6 border-l-4 h-full flex flex-col justify-center ${!showOwnedList && !enrichedLeads 
                  ? 'border-brand-500 bg-white ring-2 ring-brand-500/20 shadow-xl transform scale-[1.02] z-10' 
                  : 'border-slate-200 bg-slate-50 text-slate-500 hover:bg-white hover:border-brand-200 hover:shadow-md transition-all duration-200 cursor-pointer'
              }`}>
                <p className="text-sm font-bold uppercase flex items-center gap-2">
                    New Leads 
                    {!showOwnedList && !enrichedLeads && <span className="w-2 h-2 rounded-full bg-brand-500 animate-pulse"/>}
                </p>
                <div className="flex items-baseline gap-2 mt-1">
                    <p className={`text-3xl font-bold ${!showOwnedList && !enrichedLeads ? 'text-brand-600' : 'text-slate-700'}`}>
                        {scanResult.new_count}
                    </p>
                    <span className="text-xs opacity-70">Available</span>
                </div>
              </Card>
            </div>

            {/* TAB: OWNED LEADS */}
            <div onClick={toggleToOwned} className="group h-full">
              <Card className={`p-6 border-l-4 h-full flex flex-col justify-center ${showOwnedList 
                  ? 'border-blue-500 bg-white ring-2 ring-blue-500/20 shadow-xl transform scale-[1.02] z-10' 
                  : 'border-slate-200 bg-slate-50 text-slate-500 hover:bg-white hover:border-blue-200 hover:shadow-md transition-all duration-200 cursor-pointer'
              }`}>
                <div className="flex justify-between items-start w-full">
                  <div>
                    <p className="text-sm font-bold uppercase flex items-center gap-2">
                        Already Owned
                        {showOwnedList && <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"/>}
                    </p>
                    <div className="flex items-baseline gap-2 mt-1">
                        <p className={`text-3xl font-bold ${showOwnedList ? 'text-blue-600' : 'text-slate-700'}`}>
                            {scanResult.purchased_count}
                        </p>
                        <span className="text-xs opacity-70">In Database</span>
                    </div>
                  </div>
                  <div className={`p-2 rounded-full transition-colors ${showOwnedList ? 'bg-blue-100 text-blue-600' : 'bg-slate-200 text-slate-400 group-hover:bg-slate-300'}`}>
                     <RefreshCw size={18} />
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* DYNAMIC CONTENT AREA */}
          {enrichedLeads ? (
            /* SUCCESS VIEW */
            <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
                <div className="flex items-center justify-between bg-green-50 p-4 rounded-xl border border-green-100">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-green-100 text-green-700 rounded-lg"><CheckCircle2 size={24} /></div>
                        <div>
                            <h2 className="text-lg font-bold text-slate-900">Success! {enrichedLeads.length} leads processed.</h2>
                            <p className="text-xs text-slate-500">Your database has been updated.</p>
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <Button variant="outline" onClick={handleBackToResults}>
                            <ArrowLeft size={16} className="mr-2" /> Back
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
                        <td className="px-6 py-4 text-slate-800 font-medium whitespace-normal break-words max-w-[180px]">{lead.owner_name}</td>
                        <td className="px-6 py-4 font-bold text-green-700">${(lead.equity_value || 0).toLocaleString()}</td>
                        <td className="px-6 py-4 text-slate-600">${(lead.estimated_value || 0).toLocaleString()}</td>
                        <td className="px-6 py-4 text-slate-600">{lead.beds}</td>
                        <td className="px-6 py-4 text-slate-600">{lead.baths}</td>
                        <td className="px-6 py-4 text-slate-600 font-medium">{lead.sq_ft ? lead.sq_ft.toLocaleString() : '-'}</td>
                        <td className="px-6 py-4 text-slate-600">{lead.year_built}</td>
                        
                        {/* PHONE NUMBERS WITH N/A */}
                        <td className="px-6 py-4">
                            <div className="flex flex-col gap-1">
                                {lead.phone_numbers && lead.phone_numbers.length > 0 ? (
                                    lead.phone_numbers.map((p, idx) => (
                                        <span key={`p-${idx}`} className="text-xs font-mono text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded w-fit">{p}</span>
                                    ))
                                ) : (
                                    <span className="text-slate-400 text-xs italic">N/A</span>
                                )}
                            </div>
                        </td>

                        {/* EMAILS WITH N/A */}
                        <td className="px-6 py-4">
                            <div className="flex flex-col gap-1">
                                {lead.emails && lead.emails.length > 0 ? (
                                    lead.emails.map((e, idx) => (
                                        <span key={`e-${idx}`} className="text-xs text-slate-500 truncate max-w-[150px]" title={e}>{e}</span>
                                    ))
                                ) : (
                                    <span className="text-slate-400 text-xs italic">N/A</span>
                                )}
                            </div>
                        </td>
                        </tr>
                    ))}
                    </Table>
                </div>
            </div>

          ) : showOwnedList ? (
            /* VIEW A: OWNED LEADS (Blue Theme) */
            <Card className="p-6 bg-white border border-blue-100 shadow-sm animate-in fade-in slide-in-from-right-4 duration-300">
               <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-4">
                      <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                        <RefreshCw size={20} />
                      </div>
                      <div>
                        <h3 className="font-bold text-slate-800 text-lg">Existing Database</h3>
                        <p className="text-xs text-slate-500">Select leads to update with fresh data.</p>
                      </div>
                      
                      {selectedOwnedIds.length > 0 && (
                          <span className="ml-4 text-xs bg-blue-600 text-white px-3 py-1 rounded-full font-bold shadow-sm animate-in zoom-in">
                              {selectedOwnedIds.length} Selected
                          </span>
                      )}
                  </div>
                  
                  <div className="flex gap-3">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={handleExport} 
                        className="text-slate-600 border-slate-300 hover:bg-slate-50"
                      >
                        <Download size={16} className="mr-2" />
                        {selectedOwnedIds.length > 0 ? `Export (${selectedOwnedIds.length})` : 'Export Data'}
                      </Button>

                      <Button variant="ghost" size="sm" onClick={toggleToNew} className="text-slate-500 hover:text-slate-900">
                        Cancel
                      </Button>
                      <Button 
                        size="sm" 
                        disabled={selectedOwnedIds.length === 0}
                        onClick={() => handleEnrich(selectedOwnedIds)}
                        isLoading={isLoading}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        <RefreshCw size={16} className="mr-2" />
                        Update Selected
                      </Button>
                  </div>
               </div>
               
               <div className="bg-slate-50/50 rounded-xl border border-slate-200 overflow-hidden overflow-x-auto">
                 <table className="w-full text-left text-sm text-slate-600">
                    <thead className="bg-slate-100 border-b border-slate-200 font-bold text-slate-700 uppercase text-xs">
                        <tr>
                            <th className="px-6 py-4 w-10">
                                <input 
                                    type="checkbox" 
                                    onChange={selectAllOwned}
                                    checked={selectedOwnedIds.length === scanResult.purchased_leads.length && scanResult.purchased_leads.length > 0}
                                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                                />
                            </th>
                            {["Address", "City", "Owner", "Equity", "Value", "Beds", "Baths", "SqFt", "Year", "Phone", "Email", "Status"].map(h => (
                                <th key={h} className="px-6 py-4 whitespace-nowrap">{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 bg-white">
                        {(scanResult.purchased_leads || []).map((lead, i) => (
                          <tr key={i} className={`hover:bg-blue-50/30 transition-colors ${selectedOwnedIds.includes(lead.radar_id) ? 'bg-blue-50/50' : ''}`}>
                            <td className="px-6 py-4">
                                <input 
                                    type="checkbox" 
                                    checked={selectedOwnedIds.includes(lead.radar_id)}
                                    onChange={() => toggleOwnedSelection(lead.radar_id)}
                                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                                />
                            </td>
                            <td className="px-6 py-4 font-bold text-slate-800">{lead.address}</td>
                            <td className="px-6 py-4 text-slate-600">{lead.city}</td>
                            <td className="px-6 py-4 text-slate-800 font-medium whitespace-normal break-words max-w-[180px]">{lead.owner_name}</td>
                            <td className="px-6 py-4 text-emerald-600 font-bold">${(lead.equity_value || 0).toLocaleString()}</td>
                            <td className="px-6 py-4 text-slate-600">${(lead.estimated_value || 0).toLocaleString()}</td>
                            <td className="px-6 py-4 text-slate-600">{lead.beds}</td>
                            <td className="px-6 py-4 text-slate-600">{lead.baths}</td>
                            <td className="px-6 py-4 text-slate-600 font-medium">{lead.sq_ft ? lead.sq_ft.toLocaleString() : '-'}</td>
                            <td className="px-6 py-4 text-slate-600">{lead.year_built}</td>
                            
                            {/* PHONE NUMBERS WITH N/A */}
                            <td className="px-6 py-4">
                                <div className="flex flex-col gap-1">
                                    {lead.phone_numbers && lead.phone_numbers.length > 0 ? (
                                        lead.phone_numbers.map((p, idx) => (
                                            <span key={idx} className="text-xs font-mono text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded w-fit border border-blue-100">{p}</span>
                                        ))
                                    ) : (
                                        <span className="text-slate-400 text-xs italic">N/A</span>
                                    )}
                                </div>
                            </td>

                            {/* EMAILS WITH N/A */}
                            <td className="px-6 py-4">
                                <div className="flex flex-col gap-1">
                                    {lead.emails && lead.emails.length > 0 ? (
                                        lead.emails.map((e, idx) => (
                                            <span key={idx} className="text-xs text-slate-500 truncate max-w-[100px]" title={e}>{e}</span>
                                        ))
                                    ) : (
                                        <span className="text-slate-400 text-xs italic">N/A</span>
                                    )}
                                </div>
                            </td>

                            <td className="px-6 py-4">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                                Owned
                              </span>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                 </table>
                 {(scanResult.purchased_leads || []).length === 0 && (
                     <div className="p-12 text-center text-slate-400">
                        <p>No owned leads found in this area yet.</p>
                     </div>
                 )}
               </div>
            </Card>
          ) : (
            /* VIEW B: PURCHASE SLIDER (Brand Theme) */
            <Card className="p-8 border border-brand-100 bg-white shadow-sm animate-in fade-in slide-in-from-left-4 duration-300">
              <div className="max-w-xl mx-auto text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-brand-50 text-brand-600 mb-4">
                    <ShoppingCart size={24} />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Ready to Harvest?</h3>
                <p className="text-slate-500 mb-8">Select how many fresh leads you want to unlock from this scan.</p>
                
                <div className="bg-slate-50 p-8 rounded-2xl border border-slate-200 mb-8">
                  <div className="flex justify-between items-center mb-6">
                    <span className="text-sm font-bold text-slate-500 uppercase tracking-wide">Quantity to Buy</span>
                    <span className="text-3xl font-black text-brand-600">{purchaseLimit}</span>
                  </div>
                  
                  <input 
                    type="range" 
                    min="1" 
                    max={scanResult.new_count || 1} 
                    value={purchaseLimit}
                    onChange={(e) => setPurchaseLimit(parseInt(e.target.value))}
                    className="w-full h-3 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-500/50"
                  />
                  
                  <div className="flex justify-between text-xs font-medium text-slate-400 mt-3">
                    <span>1 Lead</span>
                    <span>{scanResult.new_count} Available</span>
                  </div>
                </div>
                
                <div className="flex justify-center gap-4">
                  <Button variant="outline" onClick={() => setScanResult(null)} className="px-6">
                    Cancel Scan
                  </Button>
                  <Button onClick={() => handleEnrich(null)} isLoading={isLoading} className="px-8 py-3 text-lg shadow-lg shadow-brand-200">
                    <ShoppingCart size={20} className="mr-2" />
                    Unlock {purchaseLimit} Leads
                  </Button>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
