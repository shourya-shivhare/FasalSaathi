import { DashboardPage } from '../features/dashboard/DashboardPage';
import { ChatPage } from '../features/chat/ChatPage';
import { FieldsPage } from '../features/fields/FieldsPage';
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
    path: '/fields',
    component: FieldsPage,
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
    path: '/onboarding',
    component: OnboardingFlow,
    protected: false,
  },
];
