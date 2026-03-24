import React from 'react';
import { Wifi, WifiOff } from 'lucide-react';
import { Badge } from '../ui/Badge';

const SyncStatus = ({ isOnline = true, lastSync }) => {
  const formatLastSync = (date) => {
    if (!date) return '';
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`flex items-center gap-1 ${isOnline ? 'text-green-600' : 'text-stone-400'}`}>
        {isOnline ? (
          <Wifi className="w-4 h-4" />
        ) : (
          <WifiOff className="w-4 h-4" />
        )}
        <span className="text-xs font-medium">
          {isOnline ? 'Online' : 'Offline'}
        </span>
      </div>
      
      {lastSync && (
        <span className="text-xs text-stone-500">
          {formatLastSync(lastSync)}
        </span>
      )}
    </div>
  );
};

export { SyncStatus };
