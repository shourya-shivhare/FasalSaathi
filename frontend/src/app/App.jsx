import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProviders } from './providers';
import { BottomNav } from '../components/layout/BottomNav';
import { ErrorBoundary } from '../components/shared/ErrorBoundary';
import { routes } from './routes';
import { useUserStore } from '../stores/useUserStore.jsx';

// Import page components
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { ChatPage } from '../features/chat/ChatPage';
import { FieldsPage } from '../features/fields/FieldsPage';
import { MarketPage } from '../features/market/MarketPage';
import { AdvisoryPage } from '../features/advisory/AdvisoryPage';
import { OnboardingFlow } from '../features/onboarding/OnboardingFlow';

const AppContent = () => {
  const { isOnboarded } = useUserStore();
  const [showOnboarding, setShowOnboarding] = useState(!isOnboarded);

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
  };

  // Show onboarding if not completed
  if (showOnboarding) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />;
  }

  return (
    <div className="relative min-h-screen bg-stone-50">
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/fields" element={<FieldsPage />} />
        <Route path="/market" element={<MarketPage />} />
        <Route path="/advisory" element={<AdvisoryPage />} />
        <Route path="/onboarding" element={<OnboardingFlow onComplete={handleOnboardingComplete} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      
      {/* Bottom Navigation */}
      <BottomNav />
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
