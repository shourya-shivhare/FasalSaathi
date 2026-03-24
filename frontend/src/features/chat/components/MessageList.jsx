import React, { useEffect, useRef } from 'react';
import { MessageBubble, TypingBubble } from './MessageBubble';

// Groups messages by date for date separators
const getDateLabel = (date) => {
  const d = date instanceof Date ? date : new Date(date);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  if (d.toDateString() === today.toDateString()) return 'Today';
  if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' });
};

const DateSeparator = ({ label }) => (
  <div className="flex items-center justify-center my-4">
    <span
      className="text-xs text-stone-500 px-3 py-1 rounded-full"
      style={{ background: 'rgba(120,113,108,0.12)' }}
    >
      {label}
    </span>
  </div>
);

const MessageList = ({ messages, isThinking }) => {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  // Build a flat list with date separators injected
  const items = [];
  let lastDate = null;
  messages.forEach((msg) => {
    const msgDate = (msg.timestamp instanceof Date ? msg.timestamp : new Date(msg.timestamp)).toDateString();
    if (msgDate !== lastDate) {
      items.push({ type: 'date', label: getDateLabel(msg.timestamp), key: `date-${msgDate}` });
      lastDate = msgDate;
    }
    items.push({ type: 'message', msg, key: msg.id });
  });

  return (
    <div
      className="flex-1 overflow-y-auto px-3 py-2"
      style={{
        backgroundImage:
          'radial-gradient(circle at 1px 1px, rgba(22,163,74,0.04) 1px, transparent 0)',
        backgroundSize: '24px 24px',
        backgroundColor: '#f0fdf4',
      }}
    >
      {items.map((item) =>
        item.type === 'date' ? (
          <DateSeparator key={item.key} label={item.label} />
        ) : (
          <MessageBubble key={item.key} message={item.msg} />
        )
      )}

      {isThinking && <TypingBubble />}

      <div ref={endRef} className="h-2" />
    </div>
  );
};

export { MessageList };
