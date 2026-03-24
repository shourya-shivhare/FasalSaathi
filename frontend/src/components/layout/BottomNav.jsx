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

const BottomNav = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isThinking } = useChatStore();

  const navItems = [
    {
      path: '/',
      label: 'Home',
      icon: LayoutDashboard,
    },
    {
      path: '/chat',
      label: 'Chat',
      icon: MessageCircle,
      showDot: isThinking,
    },
    {
      path: '/fields',
      label: 'Fields',
      icon: Map,
    },
    {
      path: '/market',
      label: 'Market',
      icon: TrendingUp,
    },
    {
      path: '/advisory',
      label: 'Advisory',
      icon: BookOpen,
    },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-stone-200 z-40">
      <div className="flex items-center justify-around py-3">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`flex flex-col items-center gap-1 min-w-[48px] py-2 px-3 rounded-lg transition-colors ${
                isActive
                  ? 'text-brand-700'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              <div className="relative">
                <Icon
                  className={`w-6 h-6 ${
                    isActive ? 'fill-current' : ''
                  }`}
                />
                {item.showDot && (
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                )}
              </div>
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export { BottomNav };
