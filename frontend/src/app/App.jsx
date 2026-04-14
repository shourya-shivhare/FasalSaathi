import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { AppProviders } from './providers';
import { Sidebar } from '../components/layout/Sidebar';
import { ErrorBoundary } from '../components/shared/ErrorBoundary';
import { useUserStore } from '../stores/useUserStore.jsx';
import { useThemeStore } from '../stores/useThemeStore.jsx';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { ChatPage } from '../features/chat/ChatPage';
import { ProfilePage } from '../features/profile/ProfilePage';
import { MarketPage } from '../features/market/MarketPage';
import { OnboardingFlow } from '../features/onboarding/OnboardingFlow';
import { SchemesPage } from '../features/schemes/SchemesPage';
import { CropSuggestionPage } from '../features/crop-suggestion/CropSuggestionPage';
import { LoginPage } from '../features/auth/LoginPage';
import { SignupPage } from '../features/auth/SignupPage';
import Home from '../pages/Home';
import ScanPage from '../pages/scan/ScanPage';

function RequireAuth({ children }) {
  const accessToken = useUserStore((s) => s.accessToken);
  if (!accessToken) return <Navigate to="/login" replace />;
  return children;
}

/** Logged-in users skip login/signup (onboarding vs dashboard depends on `isOnboarded`). */
function RequireGuest({ children }) {
  const accessToken = useUserStore((s) => s.accessToken);
  const isOnboarded = useUserStore((s) => s.isOnboarded);
  if (accessToken && isOnboarded) return <Navigate to="/dashboard" replace />;
  if (accessToken && !isOnboarded) return <Navigate to="/onboarding" replace />;
  return children;
}

function RequireSessionForOnboarding({ children }) {
  const accessToken = useUserStore((s) => s.accessToken);
  const isOnboarded = useUserStore((s) => s.isOnboarded);
  if (!accessToken) return <Navigate to="/login" replace />;
  if (isOnboarded) return <Navigate to="/dashboard" replace />;
  return children;
}

const AppContent = () => {
  const fetchCurrentUser = useUserStore((s) => s.fetchCurrentUser);
  const accessToken = useUserStore((s) => s.accessToken);
  const { initTheme } = useThemeStore();
  const location = useLocation();
  const navigate = useNavigate();

  const noSidebarRoutes = ['/', '/onboarding', '/login', '/signup'];
  const showSidebar = !noSidebarRoutes.includes(location.pathname);

  useEffect(() => {
    initTheme();
  }, [initTheme]);

  useEffect(() => {
    if (accessToken) fetchCurrentUser();
  }, [accessToken, fetchCurrentUser]);

  const handleOnboardingComplete = () => {
    navigate('/dashboard');
  };

  if (!showSidebar) {
    return (
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<RequireGuest><LoginPage /></RequireGuest>} />
        <Route path="/signup" element={<RequireGuest><SignupPage /></RequireGuest>} />
        <Route
          path="/onboarding"
          element={(
            <RequireSessionForOnboarding>
              <OnboardingFlow onComplete={handleOnboardingComplete} />
            </RequireSessionForOnboarding>
          )}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  return (
    <RequireAuth>
      <div className="app-shell">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/detect" element={<ScanPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/market" element={<MarketPage />} />
            <Route path="/schemes" element={<SchemesPage />} />
            <Route path="/crop-suggestion" element={<CropSuggestionPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </RequireAuth>
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
