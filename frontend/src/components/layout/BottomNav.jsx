import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageCircle,
  Map,
  TrendingUp,
  BookOpen,
} from 'lucide-react';
import { useChatStore } from '../../stores/useChatStore.jsx';

const navItems = [
  { path: '/',         label: 'Home',     icon: LayoutDashboard },
  { path: '/chat',     label: 'Chat',     icon: MessageCircle, dot: true },
  { path: '/fields',   label: 'Fields',   icon: Map },
  { path: '/market',   label: 'Market',   icon: TrendingUp },
  { path: '/advisory', label: 'Advisory', icon: BookOpen },
];

const BottomNav = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isThinking } = useChatStore();

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around"
      style={{
        height: '64px',
        background: '#ffffff',
        borderTop: '2px solid #bbf7d0',
        paddingBottom: 'env(safe-area-inset-bottom)',
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
                style={
                  active
                    ? { background: 'linear-gradient(135deg,#16a34a,#15803d)' }
                    : {}
                }
              >
                <Icon
                  className="w-5 h-5 transition-colors"
                  style={{ color: active ? '#ffffff' : '#78716c' }}
                />
              </div>
              {dot && isThinking && (
                <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              )}
            </div>
            <span
              className="text-[10px] font-semibold transition-colors"
              style={{ color: active ? '#16a34a' : '#a8a29e' }}
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
