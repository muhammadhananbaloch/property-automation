import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, History, MessageSquare, Settings } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation(); // Tells us which page we are currently on

  const navItems = [
    { icon: <LayoutDashboard size={20} />, label: "Dashboard", path: "/" },
    { icon: <History size={20} />, label: "History", path: "/history" },
    { icon: <MessageSquare size={20} />, label: "Campaigns", path: "/campaigns" },
    { icon: <Settings size={20} />, label: "Settings", path: "/settings" },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen fixed left-0 top-0 z-50">
      
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-100">
        <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center mr-3 shadow-sm">
          <span className="text-white font-bold text-lg">P</span>
        </div>
        <span className="font-bold text-slate-800 text-lg tracking-tight">PropAuto</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          // Check if this link is the active one
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive 
                  ? "bg-brand-50 text-brand-700 shadow-sm ring-1 ring-brand-200" 
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              }`}
            >
              {item.icon}
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300"></div>
          <div>
            <p className="text-sm font-semibold text-slate-700">Admin User</p>
            <p className="text-xs text-slate-500">Pro License</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
