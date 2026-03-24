import React from 'react';
import { ActionCard } from './ActionCard';

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';
  const isAgent = message.role === 'agent';

  const formatTimestamp = (date) => {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} min ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    
    const days = Math.floor(hours / 24);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  };

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-brand-700 text-white rounded-2xl rounded-bl-2xl px-4 py-3 shadow-sm">
          <p className="text-sm leading-relaxed">{message.text}</p>
          <div className="text-xs text-brand-200 mt-1 text-right">
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      </div>
    );
  }

  if (isAgent) {
    return (
      <div className="flex gap-3">
        <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center flex-shrink-0">
          <span className="text-white text-sm font-bold">FS</span>
        </div>
        
        <div className="flex-1 max-w-[80%] space-y-3">
          <div className="bg-stone-100 text-stone-900 rounded-2xl rounded-br-2xl px-4 py-3 shadow-sm">
            <p className="text-sm leading-relaxed">{message.text}</p>
            <div className="text-xs text-stone-500 mt-1">
              {formatTimestamp(message.timestamp)}
            </div>
          </div>
          
          {message.actionCard && (
            <ActionCard actionCard={message.actionCard} />
          )}
        </div>
      </div>
    );
  }

  return null;
};

export { MessageBubble };
