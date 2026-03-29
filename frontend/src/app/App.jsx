import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { AppProviders } from './providers';
import { BottomNav } from '../components/layout/BottomNav';
import { ErrorBoundary } from '../components/shared/ErrorBoundary';
import { routes } from './routes';
import { useUserStore } from '../stores/useUserStore.jsx';
import { useThemeStore } from '../stores/useThemeStore.jsx';

// Import page components
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { ChatPage } from '../features/chat/ChatPage';
import { ProfilePage } from '../features/profile/ProfilePage';
import { MarketPage } from '../features/market/MarketPage';
import { AdvisoryPage } from '../features/advisory/AdvisoryPage';
import { OnboardingFlow } from '../features/onboarding/OnboardingFlow';
import Home from '../pages/Home';
import ScanPage from '../pages/scan/ScanPage';

const AppContent = () => {
  const { isOnboarded } = useUserStore();
  const { initTheme } = useThemeStore();
  const location = useLocation();
  const navigate = useNavigate();
  const hideBottomNav = location.pathname === '/' || location.pathname === '/onboarding';

  useEffect(() => {
    initTheme();
  }, [initTheme]);

  const handleOnboardingComplete = () => {
    navigate('/dashboard');
  };

  return (
    <div className="relative min-h-screen theme-bg-primary transition-colors duration-300">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/market" element={<MarketPage />} />
        <Route path="/advisory" element={<AdvisoryPage />} />
        <Route path="/onboarding" element={<OnboardingFlow onComplete={handleOnboardingComplete} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      
      {/* Bottom Navigation */}
      {!hideBottomNav && <BottomNav />}
    </div>
  );
};

const App = () => {
  return (
    <ErrorBoundary>
      <AppProviders>
        <Router>
          <AppContent />
        </Router>
      </AppProviders>
    </ErrorBoundary>
  );
};

export { App };
