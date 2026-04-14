import { DashboardPage } from '../features/dashboard/DashboardPage';
import { ChatPage } from '../features/chat/ChatPage';
import { ProfilePage } from '../features/profile/ProfilePage';
import { MarketPage } from '../features/market/MarketPage';
import { AdvisoryPage } from '../features/advisory/AdvisoryPage';
import { OnboardingFlow } from '../features/onboarding/OnboardingFlow';

export const routes = [
  {
    path: '/',
    component: DashboardPage,
    protected: true,
  },
  {
    path: '/chat',
    component: ChatPage,
    protected: true,
  },
  {
    path: '/profile',
    component: ProfilePage,
    protected: true,
  },
  {
    path: '/market',
    component: MarketPage,
    protected: true,
  },
  {
    path: '/advisory',
    component: AdvisoryPage,
    protected: true,
  },
  {
    path: '/detect',
    component: () => null, // Placeholder since ScanPage isn't imported here
    protected: true,
  },
  {
    path: '/onboarding',
    component: OnboardingFlow,
    protected: false,
  },
];
