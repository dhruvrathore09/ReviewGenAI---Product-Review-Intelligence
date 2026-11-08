import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import Home from './pages/Home';
import ProductExplorer from './pages/ProductExplorer';
import ProductDetails from './pages/ProductDetails';
import ReviewAnalytics from './pages/ReviewAnalytics';
import AIAssistant from './pages/AIAssistant';

function AppContent() {
  const location = useLocation();
  const isAssistant = location.pathname.startsWith('/assistant');

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: isAssistant ? '100vh' : 'auto',
      minHeight: '100vh',
      overflow: isAssistant ? 'hidden' : 'visible',
      backgroundColor: 'var(--bg-primary)',
    }}>
      <Navbar />
      <main style={{
        flex: 1,
        overflow: isAssistant ? 'hidden' : 'visible',
        display: isAssistant ? 'flex' : 'block',
        flexDirection: isAssistant ? 'column' : 'initial',
      }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<ProductExplorer />} />
          <Route path="/products/:productId" element={<ProductDetails />} />
          <Route path="/analytics" element={<ReviewAnalytics />} />
          <Route path="/assistant" element={<AIAssistant />} />
        </Routes>
      </main>
      {!isAssistant && <Footer />}
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}
