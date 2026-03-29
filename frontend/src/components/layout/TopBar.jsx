import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bell, Search, Moon, Sun, LogOut } from 'lucide-react';
import { useThemeStore } from '../../stores/useThemeStore.jsx';
import { useUserStore } from '../../stores/useUserStore.jsx';

const TopBar = ({
  icon: Icon,
  title,
  subtitle,
  showBack = false,
  rightAction,
}) => {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useThemeStore();
  const { resetOnboarding } = useUserStore();
  const isDark = theme === 'dark';

  const handleLogout = () => {
    resetOnboarding();
    navigate('/');
  };

  return (
    <header
      className="fixed top-0 left-0 right-0 z-30 transition-colors duration-300"
      style={{
        background: 'var(--color-topbar-bg)',
        borderBottom: '1px solid var(--color-border)',
        boxShadow: isDark
          ? '0 1px 0 rgba(255,255,255,0.04)'
          : '0 1px 8px rgba(45,122,96,0.10)',
      }}
    >
      <div className="flex items-center justify-between h-[60px] px-4">
        {/* Left section */}
        <div className="flex items-center gap-3 min-w-0">
          {showBack && (
            <button
              onClick={() => navigate(-1)}
              className="p-1.5 rounded-lg transition-all flex-shrink-0"
              style={{ color: 'var(--color-text-primary)' }}
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}

          {/* Icon badge */}
          {Icon && (
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{
                background: 'var(--color-section-header-bg)',
                border: '1px solid var(--color-border)',
              }}
            >
              <Icon className="w-5 h-5" style={{ color: 'var(--color-accent-primary)' }} />
            </div>
          )}

          <div className="min-w-0">
            <h1
              className="font-bold text-[15px] leading-tight truncate tracking-tight transition-colors"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {title}
            </h1>
            {subtitle && (
              <p
                className="text-[11px] truncate mt-0.5 transition-colors"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                {subtitle}
              </p>
            )}
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg transition-all"
            style={{ color: 'var(--color-accent-primary)' }}
            title="Toggle theme"
          >
            {isDark ? <Sun className="w-[20px] h-[20px]" /> : <Moon className="w-[18px] h-[18px]" />}
          </button>

          <button
            onClick={handleLogout}
            className="p-2 rounded-lg transition-all"
            style={{ color: 'var(--color-danger)' }}
            title="Demo Logout"
          >
            <LogOut className="w-[18px] h-[18px]" />
          </button>

          {rightAction ?? (
            <>
              <button
                className="p-2 rounded-lg transition-all"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                <Search className="w-[18px] h-[18px]" />
              </button>
              <button
                className="relative p-2 rounded-lg transition-all"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                <Bell className="w-[18px] h-[18px]" />
                <span
                  className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full"
                  style={{ backgroundColor: 'var(--color-danger)' }}
                />
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export { TopBar };
