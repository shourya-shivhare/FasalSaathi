import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bell, Search } from 'lucide-react';

const TopBar = ({
  icon: Icon,
  title,
  subtitle,
  showBack = false,
  rightAction,
}) => {
  const navigate = useNavigate();

  return (
    <header
      className="fixed top-0 left-0 right-0 z-30"
      style={{
        background: 'linear-gradient(135deg, #16a34a 0%, #15803d 60%, #166534 100%)',
        boxShadow: '0 4px 20px rgba(22,163,74,0.25)',
      }}
    >
      <div className="flex items-center justify-between h-[60px] px-4">
        {/* Left section */}
        <div className="flex items-center gap-3 min-w-0">
          {showBack && (
            <button
              onClick={() => navigate(-1)}
              className="p-1.5 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all flex-shrink-0"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}

          {/* Icon badge */}
          {Icon && (
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ background: 'rgba(255,255,255,0.15)' }}
            >
              <Icon className="w-5 h-5 text-white" />
            </div>
          )}

          <div className="min-w-0">
            <h1 className="text-white font-bold text-[15px] leading-tight truncate tracking-tight">
              {title}
            </h1>
            {subtitle && (
              <p className="text-green-200/80 text-[11px] truncate mt-0.5">{subtitle}</p>
            )}
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-0.5 flex-shrink-0">
          {rightAction ?? (
            <>
              <button className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all">
                <Search className="w-[18px] h-[18px]" />
              </button>
              <button className="relative p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all">
                <Bell className="w-[18px] h-[18px]" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-400 rounded-full ring-2 ring-green-700" />
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export { TopBar };
