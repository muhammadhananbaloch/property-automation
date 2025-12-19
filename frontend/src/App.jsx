import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';

// Import our new pages
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Campaigns from './pages/Campaigns';

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          {/* When URL is "/", show Dashboard */}
          <Route path="/" element={<Dashboard />} />
          
          {/* When URL is "/history", show History */}
          <Route path="/history" element={<History />} />
          
          {/* When URL is "/campaigns", show Campaigns */}
          <Route path="/campaigns" element={<Campaigns />} />
          
          {/* Catch-all: If URL is weird, go back home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
}

export default App;
