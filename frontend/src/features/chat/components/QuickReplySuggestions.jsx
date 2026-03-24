import React from 'react';
import { motion } from 'framer-motion';

const QuickReplySuggestions = ({ suggestions, onSuggestionClick }) => {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div
      className="px-3 py-2 flex gap-2 overflow-x-auto no-scrollbar"
      style={{ background: '#ffffff', borderTop: '1px solid #f0fdf4' }}
    >
      {suggestions.map((s, i) => (
        <motion.button
          key={i}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          onClick={() => onSuggestionClick(s)}
          className="flex-shrink-0 text-xs font-medium px-3 py-1.5 rounded-full border active:scale-95 transition-all"
          style={{
            color: '#16a34a',
            borderColor: '#bbf7d0',
            background: '#f0fdf4',
            whiteSpace: 'nowrap',
          }}
        >
          {s}
        </motion.button>
      ))}
    </div>
  );
};

export { QuickReplySuggestions };
