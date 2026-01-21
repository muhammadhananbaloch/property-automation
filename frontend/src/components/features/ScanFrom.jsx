import React, { useState, useEffect, useRef } from 'react';
import { Search, MapPin, ChevronDown } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';

// 1. Full List of US States (Code -> Name)
const US_STATES = [
  { code: 'AL', name: 'Alabama' }, { code: 'AK', name: 'Alaska' }, { code: 'AZ', name: 'Arizona' },
  { code: 'AR', name: 'Arkansas' }, { code: 'CA', name: 'California' }, { code: 'CO', name: 'Colorado' },
  { code: 'CT', name: 'Connecticut' }, { code: 'DE', name: 'Delaware' }, { code: 'DC', name: 'District Of Columbia' },
  { code: 'FL', name: 'Florida' }, { code: 'GA', name: 'Georgia' }, { code: 'HI', name: 'Hawaii' },
  { code: 'ID', name: 'Idaho' }, { code: 'IL', name: 'Illinois' }, { code: 'IN', name: 'Indiana' },
  { code: 'IA', name: 'Iowa' }, { code: 'KS', name: 'Kansas' }, { code: 'KY', name: 'Kentucky' },
  { code: 'LA', name: 'Louisiana' }, { code: 'ME', name: 'Maine' }, { code: 'MD', name: 'Maryland' },
  { code: 'MA', name: 'Massachusetts' }, { code: 'MI', name: 'Michigan' }, { code: 'MN', name: 'Minnesota' },
  { code: 'MS', name: 'Mississippi' }, { code: 'MO', name: 'Missouri' }, { code: 'MT', name: 'Montana' },
  { code: 'NE', name: 'Nebraska' }, { code: 'NV', name: 'Nevada' }, { code: 'NH', name: 'New Hampshire' },
  { code: 'NJ', name: 'New Jersey' }, { code: 'NM', name: 'New Mexico' }, { code: 'NY', name: 'New York' },
  { code: 'NC', name: 'North Carolina' }, { code: 'ND', name: 'North Dakota' }, { code: 'OH', name: 'Ohio' },
  { code: 'OK', name: 'Oklahoma' }, { code: 'OR', name: 'Oregon' }, { code: 'PA', name: 'Pennsylvania' },
  { code: 'RI', name: 'Rhode Island' }, { code: 'SC', name: 'South Carolina' }, { code: 'SD', name: 'South Dakota' },
  { code: 'TN', name: 'Tennessee' }, { code: 'TX', name: 'Texas' }, { code: 'UT', name: 'Utah' },
  { code: 'VT', name: 'Vermont' }, { code: 'VA', name: 'Virginia' }, { code: 'WA', name: 'Washington' },
  { code: 'WV', name: 'West Virginia' }, { code: 'WI', name: 'Wisconsin' }, { code: 'WY', name: 'Wyoming' }
];

// 2. Major Cities for Predictive Search (Mapped by State CODE)
const KNOWN_CITIES = {
  "VA": ["Richmond", "Virginia Beach", "Norfolk", "Chesapeake", "Arlington", "Alexandria", "Newport News", "Hampton", "Roanoke"],
  "CA": ["Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno", "Sacramento", "Long Beach", "Oakland", "Bakersfield", "Anaheim"],
  "TX": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso", "Arlington"],
  "FL": ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg", "Hialeah"],
  "NY": ["New York", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany"],
  "IL": ["Chicago", "Aurora", "Naperville", "Joliet", "Rockford", "Springfield"],
  "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading"],
  "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron", "Dayton"],
  "GA": ["Atlanta", "Augusta", "Columbus", "Macon", "Savannah", "Athens"],
  "NC": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem", "Fayetteville"],
  "MI": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor", "Lansing"]
};

// 3. Investment Strategies (Matching Backend CriteriaMapper)
const STRATEGIES = [
  { value: 'pre_foreclosure', label: 'Pre-Foreclosure' },
  { value: 'tax_delinquent', label: 'Tax Delinquent' },
  { value: 'vacant', label: 'Vacant Land/Site' },
  { value: 'absentee', label: 'Absentee Owner' },
  { value: 'inherited', label: 'Inherited Property' }
];

export const ScanForm = ({ onScan, isLoading }) => {
  // State
  const [formData, setFormData] = useState({
    state: 'VA', // Defaulting to VA code
    city: '',
    strategy: 'pre_foreclosure'
  });

  // Predictive UI State
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const wrapperRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef]);

  // Handle City Input Typing
  const handleCityChange = (e) => {
    const input = e.target.value;
    setFormData({ ...formData, city: input });

    if (input.length > 0) {
      // Get cities for the currently selected state code
      const stateCities = KNOWN_CITIES[formData.state] || [];
      
      // Filter matches (case-insensitive)
      const filtered = stateCities.filter(city => 
        city.toLowerCase().startsWith(input.toLowerCase())
      );
      
      setSuggestions(filtered);
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  // Handle Suggestion Click
  const selectCity = (city) => {
    setFormData({ ...formData, city: city });
    setShowSuggestions(false);
  };

  // Submit Handler
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.city || !formData.state) return;

    // CRITICAL: Format data for API Compliance
    const formattedData = {
        state: formData.state,
        city: formData.city.toUpperCase().trim(),
        strategy: formData.strategy
    };

    onScan(formattedData);
  };

  return (
    <Card className="max-w-2xl mx-auto p-8 bg-white shadow-xl border border-slate-100">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-brand-50 rounded-full flex items-center justify-center mx-auto mb-4 text-brand-600">
          <Search size={32} />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">Start New Scan</h2>
        <p className="text-slate-500">Enter a target area to harvest property leads.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-6">
          
          {/* State Selection */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">State</label>
            <div className="relative">
              <select 
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg appearance-none text-slate-700 font-medium focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all cursor-pointer"
                value={formData.state}
                onChange={(e) => setFormData({...formData, state: e.target.value, city: ''})} 
              >
                {US_STATES.map((state) => (
                  <option key={state.code} value={state.code}>
                    {state.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-3.5 text-slate-400 pointer-events-none" size={16} />
            </div>
          </div>

          {/* Strategy Selection */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Strategy</label>
            <div className="relative">
              <select 
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg appearance-none text-slate-700 font-medium focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all cursor-pointer"
                value={formData.strategy}
                onChange={(e) => setFormData({...formData, strategy: e.target.value})}
              >
                {STRATEGIES.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-3.5 text-slate-400 pointer-events-none" size={16} />
            </div>
          </div>
        </div>

        {/* City Input with Predictive Search */}
        <div className="space-y-2 relative" ref={wrapperRef}>
          <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Target City</label>
          <div className="relative">
            <MapPin className="absolute left-3 top-3.5 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder={`e.g. ${KNOWN_CITIES[formData.state]?.[0] || 'City Name'}`}
              className="w-full pl-10 p-3 bg-white border border-slate-200 rounded-lg text-slate-900 placeholder:text-slate-300 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all"
              value={formData.city}
              onChange={handleCityChange}
              onFocus={() => formData.city && setShowSuggestions(true)}
            />
          </div>

          {/* Suggestions Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <ul className="absolute z-10 w-full bg-white border border-slate-200 rounded-lg shadow-lg max-h-60 overflow-auto mt-1 animate-in fade-in zoom-in-95 duration-100">
              {suggestions.map((city, index) => (
                <li 
                  key={index}
                  onClick={() => selectCity(city)}
                  className="px-4 py-2 hover:bg-brand-50 text-slate-700 cursor-pointer font-medium flex items-center gap-2 border-b border-slate-50 last:border-0"
                >
                  <MapPin size={14} className="text-slate-400" />
                  {city}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* FIXED BUTTON: Removed inner <Loader2> to prevent double animation */}
        <Button 
          type="submit" 
          isLoading={isLoading} 
          disabled={!formData.city}
          className="w-full py-4 text-lg shadow-lg shadow-brand-200"
        >
          {isLoading ? 'Scanning...' : 'Launch Scan'}
        </Button>
      </form>
    </Card>
  );
};
