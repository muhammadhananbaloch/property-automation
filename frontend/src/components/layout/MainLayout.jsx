import React from 'react';
import Sidebar from './Sidebar';

const MainLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* The Sidebar is fixed on the left */}
      <Sidebar />
      
      {/* The Main Content Area - pushed 64 units (16rem) to the right */}
      <main className="ml-64 min-h-screen">
        {children}
      </main>
    </div>
  );
};

export default MainLayout;
