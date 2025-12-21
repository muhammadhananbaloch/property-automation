import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

export const ScanForm = ({ onScan, isLoading }) => {
  // 1. Local State for the inputs
  const [formData, setFormData] = useState({
    state: 'VA', // Default to VA for ease
    city: '',
    strategy: 'pre_foreclosure'
  });

  // 2. Handle typing
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // 3. Handle Submit
  const handleSubmit = (e) => {
    e.preventDefault(); // Stop page reload
    // Send data back to the parent component
    onScan(formData);
  };

  return (
    <Card className="max-w-xl mx-auto p-8">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-brand-50 text-brand-600 mb-4">
          <Search size={24} />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Start New Scan</h2>
        <p className="text-slate-500 text-sm mt-1">
          Enter a target area to harvest property leads.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          {/* State Input */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">State</label>
            <select
              name="state"
              value={formData.state}
              onChange={handleChange}
              className="px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 text-sm bg-white"
            >
              <option value="VA">Virginia</option>
              <option value="CA">California</option>
              <option value="TX">Texas</option>
              <option value="FL">Florida</option>
            </select>
          </div>

          {/* Strategy Input */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Strategy</label>
            <select
              name="strategy"
              value={formData.strategy}
              onChange={handleChange}
              className="px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 text-sm bg-white"
            >
              <option value="pre_foreclosure">Pre-Foreclosure</option>
              <option value="auction">Auction</option>
              <option value="cash_buyer">Cash Buyer</option>
            </select>
          </div>
        </div>

        {/* City Input */}
        <Input 
          label="Target City"
          placeholder="e.g. Richmond"
          value={formData.city}
          onChange={(e) => setFormData({...formData, city: e.target.value})}
        />

        <div className="pt-2">
          <Button 
            variant="primary" 
            isLoading={isLoading} 
            disabled={!formData.city} // Disable if no city typed
            className="w-full"
          >
            Launch Scan
          </Button>
        </div>
      </form>
    </Card>
  );
};
