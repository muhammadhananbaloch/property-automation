import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  History, 
  MessageSquare, 
  Settings, 
  LogOut, 
  User 
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext'; // <--- 1. Import Auth Hook

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth(); // <--- 2. Get User & Logout function

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { icon: <LayoutDashboard size={20} />, label: "Dashboard", path: "/dashboard" },
    { icon: <History size={20} />, label: "History", path: "/history" },
    { icon: <MessageSquare size={20} />, label: "Campaigns", path: "/campaigns" },
    // You can uncomment this when you build the settings page
    // { icon: <Settings size={20} />, label: "Settings", path: "/settings" },
  ];

  return (
    // changed 'fixed' to 'sticky top-0' to work with the Flexbox MainLayout
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0 z-20">
      
      {/* --- Logo --- */}
      <div className="h-16 flex items-center px-6 border-b border-slate-100">
        <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center mr-3 shadow-sm">
          <span className="text-white font-bold text-lg">P</span>
        </div>
        <span className="font-bold text-slate-800 text-lg tracking-tight">PropAuto</span>
      </div>

      {/* --- Navigation --- */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
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

      {/* --- Footer (User Profile & Logout) --- */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center gap-3">
          
          {/* User Avatar (Initials or Icon) */}
          <div className="w-9 h-9 rounded-full bg-white border border-slate-200 flex items-center justify-center text-brand-600 shadow-sm">
             <User size={18} />
          </div>
          
          {/* User Info (Dynamic) */}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-slate-700 truncate">
                {user?.full_name || 'User'}
            </p>
            <p className="text-xs text-slate-500 truncate" title={user?.email}>
                {user?.email}
            </p>
          </div>

          {/* Logout Button */}
          <button 
            onClick={handleLogout}
            className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
            title="Sign Out"
          >
            <LogOut size={18} />
          </button>

        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
