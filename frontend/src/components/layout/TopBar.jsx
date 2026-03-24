import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bell } from 'lucide-react';
import { Badge } from '../ui/Badge';

const TopBar = ({ title, subtitle, showBack = false, rightAction }) => {
  const navigate = useNavigate();

  const defaultRightAction = (
    <button className="relative p-2 text-stone-600 hover:text-stone-800 transition-colors">
      <Bell className="w-5 h-5" />
      <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
    </button>
  );

  return (
    <div className="fixed top-0 left-0 right-0 bg-white border-b border-stone-200 z-30">
      <div className="flex items-center justify-between h-14 px-4">
        <div className="flex items-center gap-3">
          {showBack && (
            <button
              onClick={() => navigate(-1)}
              className="p-2 text-stone-600 hover:text-stone-800 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          <div>
            <h1 className="text-lg font-semibold text-stone-900">{title}</h1>
            {subtitle && (
              <p className="text-sm text-stone-500">{subtitle}</p>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {rightAction || defaultRightAction}
        </div>
      </div>
    </div>
  );
};

export { TopBar };
