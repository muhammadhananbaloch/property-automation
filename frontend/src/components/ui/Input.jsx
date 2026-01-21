import React from 'react';

export const Input = ({ 
  label, 
  className = "", 
  ...props 
}) => {
  return (
    <div className="flex flex-col gap-1.5 w-full">
      {/* Only render label if one is passed */}
      {label && (
        <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          {label}
        </label>
      )}
      <input
        className={`px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm shadow-sm placeholder-slate-400
        focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all
        disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed
        ${className}`}
        {...props} // <--- CRITICAL: Passes 'name', 'value', 'onChange', 'required'
      />
    </div>
  );
};
