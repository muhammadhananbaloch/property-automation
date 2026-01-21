import React from 'react';
import Sidebar from './Sidebar';

const MainLayout = ({ children }) => {
  return (
    // 'flex' makes the Sidebar and Main Content sit side-by-side naturally
    <div className="flex min-h-screen bg-slate-50">
      
      {/* The Sidebar (Fixed width handled inside component) */}
      <Sidebar />
      
      {/* The Main Content (Grows to fill remaining space) */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Scrollable Content Container */}
        <div className="flex-1 overflow-y-auto p-8">
          {children}
        </div>
      </main>
      
    </div>
  );
};

export default MainLayout;
