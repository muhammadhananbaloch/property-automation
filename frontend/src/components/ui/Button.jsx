import React from 'react';
import { Loader2 } from 'lucide-react';

export const Button = ({ 
  children, 
  variant = 'primary', 
  isLoading = false, 
  className = "",
  ...props // <--- CRITICAL: Captures 'type="submit"', 'onClick', 'disabled'
}) => {
  
  const baseStyles = "px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-offset-1";
  
  const variants = {
    primary: "bg-brand-600 text-white hover:bg-brand-700 focus:ring-brand-500 disabled:bg-brand-400",
    outline: "border border-slate-300 text-slate-700 hover:bg-slate-50 focus:ring-slate-200 disabled:opacity-50",
    ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500"
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${className}`}
      disabled={props.disabled || isLoading}
      {...props} // <--- Passes 'type="submit"' to the DOM element
    >
      {isLoading && <Loader2 size={16} className="animate-spin" />}
      {children}
    </button>
  );
};
