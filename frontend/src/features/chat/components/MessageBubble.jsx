import React from 'react';
import { motion } from 'framer-motion';
import { CheckCheck } from 'lucide-react';
import { ActionCard } from './ActionCard';
import { ACTION_CARD_TYPES } from '../../../lib/constants.jsx';

const formatTime = (date) => {
  if (!date) return '';
  const d = date instanceof Date ? date : new Date(date);
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
};

const TypingBubble = () => (
  <div className="flex items-end gap-2 mb-3">
    {/* Avatar */}
    <div
      className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-white text-xs font-bold shadow-sm transition-colors"
      style={{ background: 'var(--color-accent-primary)' }}
    >
      FS
    </div>

    {/* Dots bubble */}
    <div
      className="px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm transition-colors border"
      style={{ 
        background: 'var(--color-bg-secondary)', 
        borderColor: 'var(--color-border)' 
      }}
    >
      <div className="flex items-center gap-1.5 ">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-2 h-2 rounded-full"
            style={{
              backgroundColor: 'var(--color-text-secondary)',
              animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>
    </div>
  </div>
);

const UserBubble = ({ message }) => (
  <motion.div
    initial={{ opacity: 0, y: 8, scale: 0.96 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    transition={{ duration: 0.2 }}
    className="flex justify-end items-end gap-1 mb-2"
  >
    <div className="max-w-[78%] flex flex-col items-end gap-0.5">
      <div
        className="px-4 py-2.5 rounded-2xl rounded-br-sm shadow-sm text-white transition-colors"
        style={{ background: 'var(--color-accent-primary)' }}
      >
        <p className="text-sm leading-relaxed">{message.text}</p>
      </div>
      <div className="flex items-center gap-1 pr-1">
        <span className="text-[10px] opacity-60" style={{ color: 'var(--color-text-secondary)' }}>
          {formatTime(message.timestamp)}
        </span>
        <CheckCheck className="w-3.5 h-3.5" style={{ color: 'var(--color-success)' }} />
      </div>
    </div>
  </motion.div>
);

const AgentBubble = ({ message }) => (
  <motion.div
    initial={{ opacity: 0, y: 8, scale: 0.96 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    transition={{ duration: 0.2 }}
    className="flex items-end gap-2 mb-2"
  >
    {/* Avatar */}
    <div
      className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-white text-xs font-bold shadow-sm transition-colors"
      style={{ background: 'var(--color-accent-primary)' }}
    >
      FS
    </div>

    <div className="max-w-[78%] flex flex-col gap-2">
      <div
        className="px-4 py-2.5 rounded-2xl rounded-bl-sm shadow-sm transition-colors border"
        style={{ 
          background: 'var(--color-bg-secondary)', 
          borderColor: 'var(--color-border)',
        }}
      >
        <p className="text-sm leading-relaxed transition-colors" style={{ color: 'var(--color-text-primary)' }}>
          {message.text}
        </p>
        <span className="text-[10px] mt-1 block text-right opacity-60" style={{ color: 'var(--color-text-secondary)' }}>
          {formatTime(message.timestamp)}
        </span>
      </div>

      {message.actionCard && (
        <ActionCard actionCard={message.actionCard} />
      )}

      {/* Auto-detect pest-related keywords and show scan prompt */}
      {message.role === 'agent' && !message.actionCard && (
        (() => {
          const keywords = ['keeda', 'pests', 'bimari', 'scan', 'insect', 'disease', 'pesticide', 'infection'];
          const text = message.text.toLowerCase();
          if (keywords.some(kw => text.includes(kw))) {
            return (
              <ActionCard 
                actionCard={{
                  type: ACTION_CARD_TYPES.SCAN,
                  data: {
                    title: "Pest Detection Support",
                    subtitle: "Detect & treat pests instantly",
                    description: "It looks like you're talking about pests or crop issues. Try our new Scan feature to get instant identification and treatment advice."
                  }
                }} 
              />
            );
          }
          return null;
        })()
      )}
    </div>
  </motion.div>
);

const MessageBubble = ({ message, showTyping }) => {
  if (showTyping) return <TypingBubble />;
  if (message.role === 'user') return <UserBubble message={message} />;
  if (message.role === 'agent') return <AgentBubble message={message} />;
  return null;
};

export { MessageBubble, TypingBubble };
