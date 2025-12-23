import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Card } from '../components/ui/Card';
import { Table } from '../components/ui/Table';
import { Button } from '../components/ui/Button';
import { FileText, Calendar, Loader2, AlertCircle } from 'lucide-react';

const History = () => {
  const [historyItems, setHistoryItems] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  
  const [selectedBatchId, setSelectedBatchId] = useState(null);
  const [batchLeads, setBatchLeads] = useState([]);
  const [isLoadingLeads, setIsLoadingLeads] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await api.getHistory();
      setHistoryItems(data);
      if (data.length > 0) {
        handleSelectBatch(data[0].id);
      }
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleSelectBatch = async (batchId) => {
    setSelectedBatchId(batchId);
    setIsLoadingLeads(true);
    setBatchLeads([]); 

    try {
      const data = await api.getLeads(batchId);
      setBatchLeads(Array.isArray(data) ? data : data.leads || []); 
    } catch (err) {
      console.error("Failed to load leads:", err);
    } finally {
      setIsLoadingLeads(false);
    }
  };

  if (isLoadingHistory) {
    return (
      <div className="p-8 flex items-center justify-center h-screen text-slate-400">
        <Loader2 className="animate-spin mr-2" /> Loading your archives...
      </div>
    );
  }

  return (
    <div className="p-8 max-w-[1600px] mx-auto h-[calc(100vh-2rem)] flex flex-col">
      
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Search History</h1>
          <p className="text-slate-500">Revisit your past harvests.</p>
        </div>
        <Button variant="outline" onClick={loadHistory}>Refresh Data</Button>
      </div>

      <div className="flex gap-6 h-full min-h-0">
        
        {/* LEFT PANEL: FILING CABINET */}
        <Card className="w-80 flex flex-col overflow-hidden border-r border-slate-200 shadow-none rounded-r-none z-10">
          <div className="p-4 border-b border-slate-100 bg-slate-50 font-bold text-slate-700 text-sm uppercase tracking-wider">
            Past Scans
          </div>
          <div className="overflow-y-auto flex-1 p-2 space-y-2 bg-slate-50/50">
            {historyItems.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-sm">No history found.</div>
            ) : (
              historyItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleSelectBatch(item.id)}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-200 group relative ${
                    selectedBatchId === item.id
                      ? "bg-white border-brand-200 shadow-md ring-1 ring-brand-100 z-10"
                      : "bg-white/50 border-transparent hover:bg-white hover:shadow-sm"
                  }`}
                >
                  {selectedBatchId === item.id && (
                    <div className="absolute left-0 top-4 bottom-4 w-1 bg-brand-500 rounded-r-full" />
                  )}

                  <div className="flex justify-between items-start mb-2 pl-2">
                    <span className="text-xs font-bold text-slate-400">#{item.id}</span>
                    <span className="text-[10px] uppercase font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div className="pl-2">
                    <div className="font-bold text-slate-800 text-lg mb-0.5">{item.city}</div>
                    <div className="text-xs text-slate-500 capitalize mb-3">{item.strategy.replace('_', ' ')}</div>
                    
                    <div className="flex items-center text-xs font-medium text-slate-600 bg-slate-100/80 px-2 py-1.5 rounded-md w-fit">
                      <FileText size={12} className="mr-1.5 text-slate-400" />
                      {item.total_results} Leads Found
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </Card>

        {/* RIGHT PANEL: FULL DESK */}
        <Card className="flex-1 flex flex-col overflow-hidden shadow-sm rounded-l-none border-l-0">
          {selectedBatchId ? (
            <>
              <div className="p-4 border-b border-slate-200 bg-white flex justify-between items-center">
                <div className="flex items-center gap-3">
                   <div className="p-2 bg-brand-50 text-brand-600 rounded-lg">
                     <FileText size={20} />
                   </div>
                   <div>
                     <h3 className="font-bold text-slate-900">Scan Report #{selectedBatchId}</h3>
                     <p className="text-xs text-slate-500">Full data access</p>
                   </div>
                </div>
                <div className="text-sm text-slate-500">
                  Showing <span className="font-bold text-slate-900">{batchLeads.length}</span> records
                </div>
              </div>

              <div className="flex-1 overflow-auto bg-slate-50/30">
                {isLoadingLeads ? (
                  <div className="h-full flex flex-col items-center justify-center text-slate-400">
                    <Loader2 size={40} className="animate-spin mb-4 text-brand-400" />
                    <p>Retrieving property data...</p>
                  </div>
                ) : batchLeads.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-slate-400">
                    <AlertCircle size={40} className="mb-4 opacity-20" />
                    <p>No leads found in this batch.</p>
                  </div>
                ) : (
                  <div className="min-w-full inline-block align-middle p-4">
                    <div className="border rounded-xl overflow-hidden shadow-sm bg-white">
                      <Table headers={["Address", "City", "Owner", "Equity", "Value", "Beds", "Baths", "SqFt", "Year", "Phone", "Email"]}>
                        {batchLeads.map((lead, index) => (
                          <tr key={index} className="hover:bg-blue-50/50 transition-colors border-b border-slate-100 group">
                            
                            <td className="px-6 py-4 font-bold text-slate-900 text-sm">{lead.address}</td>
                            
                            <td className="px-6 py-4 text-sm text-slate-600">{lead.city}, {lead.state}</td>

                            {/* UPDATED OWNER COLUMN: Wrapped Text */}
                            <td className="px-6 py-4 text-slate-800 text-sm font-medium whitespace-normal break-words max-w-[180px]">
                                {lead.owner_name}
                            </td>

                            <td className="px-6 py-4 font-bold text-emerald-700 text-sm">
                                ${(lead.equity_value || 0).toLocaleString()}
                            </td>
                            
                            <td className="px-6 py-4 text-sm text-slate-600 font-medium">
                              ${(lead.estimated_value || 0).toLocaleString()}
                            </td>
                            
                            <td className="px-6 py-4 text-sm text-slate-600">{lead.beds}</td>
                            <td className="px-6 py-4 text-sm text-slate-600">{lead.baths}</td>
                            <td className="px-6 py-4 text-sm text-slate-600 font-medium">
                                {lead.sq_ft ? lead.sq_ft.toLocaleString() : '-'}
                            </td>
                            <td className="px-6 py-4 text-sm text-slate-600">{lead.year_built}</td>

                            {/* PHONE NUMBERS WITH N/A */}
                            <td className="px-6 py-4 align-middle">
                              <div className="flex flex-col gap-1.5">
                                {lead.phone_numbers && lead.phone_numbers.length > 0 ? (
                                  lead.phone_numbers.map((phone, i) => (
                                    <span key={i} className="inline-block text-xs font-mono text-blue-700 bg-blue-50 px-2 py-1 rounded border border-blue-100 w-fit select-all">
                                      {phone}
                                    </span>
                                  ))
                                ) : (
                                  <span className="text-slate-400 text-xs italic">N/A</span>
                                )}
                              </div>
                            </td>

                            {/* EMAILS WITH N/A */}
                            <td className="px-6 py-4 align-middle">
                              <div className="flex flex-col gap-1">
                                {lead.emails && lead.emails.length > 0 ? (
                                  lead.emails.map((email, i) => (
                                    <span key={i} className="text-xs text-slate-600 hover:text-brand-600 select-all" title={email}>{email}</span>
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
                )}
              </div>
            </>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 bg-slate-50/50">
              <FileText size={48} className="mb-4 text-slate-300" />
              <p>Select a scan from the left to view the full report.</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default History;
