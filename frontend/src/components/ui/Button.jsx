import React from 'react';
import { Loader2 } from 'lucide-react';

export const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', // Options: 'primary' (Blue) or 'outline' (White)
  isLoading = false, 
  disabled = false 
}) => {
  
  const baseStyles = "px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center justify-center gap-2";
  
  const variants = {
    primary: "bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-50",
    outline: "border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50"
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`${baseStyles} ${variants[variant]}`}
    >
      {/* Show spinner if loading */}
      {isLoading && <Loader2 size={16} className="animate-spin" />}
      {children}
    </button>
  );
};
