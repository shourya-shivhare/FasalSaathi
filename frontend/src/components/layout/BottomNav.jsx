import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageCircle,
  Map,
  TrendingUp,
  BookOpen,
  ScanLine,
  Sprout,
  User,
} from 'lucide-react';
import { useChatStore } from '../../stores/useChatStore.jsx';

const navItems = [
  { path: '/dashboard', label: 'Home', icon: LayoutDashboard },
  { path: '/chat', label: 'Chat', icon: MessageCircle, dot: true },
  { path: '/detect', label: 'Scan', icon: ScanLine },
  { path: '/crop-suggestion', label: 'Crops', icon: Sprout },
  { path: '/market', label: 'Market', icon: TrendingUp },
  { path: '/profile', label: 'Profile', icon: User },
];

const BottomNav = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isThinking } = useChatStore();

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around border-t"
      style={{
        height: '64px',
        paddingBottom: 'env(safe-area-inset-bottom)',
        backgroundColor: 'var(--color-topbar-bg)',
        borderColor: 'var(--color-border)',
        boxShadow: '0 -1px 0 rgba(0,0,0,0.06), 0 -4px 16px rgba(0,0,0,0.08)',
        isolation: 'isolate',
        backdropFilter: 'none',
      }}
    >
      {navItems.map(({ path, label, icon: Icon, dot }) => {
        const active = location.pathname === path;
        return (
          <button
            key={path}
            onClick={() => navigate(path)}
            className="flex flex-col items-center gap-0.5 px-3 py-1 rounded-xl transition-all active:scale-95"
            style={{ minWidth: '48px' }}
          >
            <div className="relative">
              <div
                className="w-8 h-8 flex items-center justify-center rounded-xl transition-all"
                style={{
                  backgroundColor: active ? 'var(--color-section-header-bg)' : 'transparent',
                }}
              >
                <Icon
                  className="w-5 h-5 transition-colors"
                  style={{
                    color: active ? 'var(--color-accent-primary)' : 'var(--color-nav-inactive)',
                  }}
                />
              </div>
              {dot && isThinking && (
                <span
                  className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full animate-pulse"
                  style={{ backgroundColor: 'var(--color-success)' }}
                />
              )}
            </div>
            <span
              className="text-[10px] font-semibold transition-colors"
              style={{
                color: active ? 'var(--color-accent-primary)' : 'var(--color-nav-inactive)',
              }}
            >
              {label}
            </span>
          </button>
        );
      })}
    </div>
  );
};

export { BottomNav };