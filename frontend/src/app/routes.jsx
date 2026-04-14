import { DashboardPage } from '../features/dashboard/DashboardPage';
import { ChatPage } from '../features/chat/ChatPage';
import { ProfilePage } from '../features/profile/ProfilePage';
import { MarketPage } from '../features/market/MarketPage';
import { SchemesPage } from '../features/schemes/SchemesPage';
import { CropSuggestionPage } from '../features/crop-suggestion/CropSuggestionPage';
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
    path: '/schemes',
    component: SchemesPage,
    protected: true,
  },
  {
    path: '/crop-suggestion',
    component: CropSuggestionPage,
    protected: true,
  },
  {
    path: '/detect',
    component: () => null,
    protected: true,
  },
  {
    path: '/onboarding',
    component: OnboardingFlow,
    protected: false,
  },
];
