import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { AppProviders } from './providers';
import { Sidebar } from '../components/layout/Sidebar';
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
import { LoginPage } from '../features/auth/LoginPage';
import { SignupPage } from '../features/auth/SignupPage';
import Home from '../pages/Home';
import ScanPage from '../pages/scan/ScanPage';

const AppContent = () => {
  const { isOnboarded } = useUserStore();
  const { initTheme } = useThemeStore();
  const location = useLocation();
  const navigate = useNavigate();

  // Pages that don't use the sidebar layout
  const noSidebarRoutes = ['/', '/onboarding', '/login', '/signup'];
  const showSidebar = !noSidebarRoutes.includes(location.pathname);

  useEffect(() => {
    initTheme();
  }, [initTheme]);

  const handleOnboardingComplete = () => {
    navigate('/dashboard');
  };

  if (!showSidebar) {
    return (
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/onboarding" element={<OnboardingFlow onComplete={handleOnboardingComplete} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/scan" element={<ScanPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/market" element={<MarketPage />} />
          <Route path="/advisory" element={<AdvisoryPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
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

