import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Paperclip, Smile } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ChatInput = ({ onSendMessage, disabled = false, isListening = false, onToggleListening }) => {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput('');
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const canSend = input.trim().length > 0 && !disabled && !isListening;

  return (
    <div
      className="relative"
      style={{
        background: '#ffffff',
        borderTop: '1px solid #e7e5e4',
        padding: '8px 12px',
        paddingBottom: 'max(8px, env(safe-area-inset-bottom))',
      }}
    >
      {/* Listening Overlay */}
      <AnimatePresence>
        {isListening && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            className="absolute bottom-full left-0 right-0 flex items-center justify-center gap-2 py-2 bg-red-50 border-t border-red-200"
          >
            <span className="flex gap-1">
              {[0, 1, 2, 3].map((i) => (
                <span
                  key={i}
                  className="w-1 rounded-full bg-red-500"
                  style={{
                    height: `${12 + Math.sin(i) * 6}px`,
                    animation: `bounce 0.8s ease-in-out ${i * 0.1}s infinite`,
                    display: 'inline-block',
                  }}
                />
              ))}
            </span>
            <span className="text-sm font-medium text-red-600">Listening…</span>
          </motion.div>
        )}
      </AnimatePresence>

      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        {/* Input pill */}
        <div
          className="flex-1 flex items-center gap-1 rounded-full px-4 py-2 min-h-[44px]"
          style={{ background: '#f4f4f5', border: '1px solid #e4e4e7' }}
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              // Auto-resize
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
            }}
            onKeyDown={handleKeyDown}
            placeholder="Message FasalSaathi…"
            disabled={disabled || isListening}
            rows={1}
            className="flex-1 bg-transparent text-sm text-stone-800 resize-none outline-none placeholder-stone-400 leading-relaxed"
            style={{ maxHeight: '120px', overflowY: 'auto' }}
          />
        </div>

        {/* Mic / Send swap button */}
        <AnimatePresence mode="wait">
          {canSend ? (
            <motion.button
              key="send"
              type="submit"
              initial={{ scale: 0, rotate: -30 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0, rotate: 30 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              className="w-11 h-11 flex items-center justify-center rounded-full text-white shadow-md active:scale-95"
              style={{ background: 'linear-gradient(135deg, #16a34a, #15803d)' }}
            >
              <Send className="w-5 h-5" />
            </motion.button>
          ) : (
            <motion.button
              key="mic"
              type="button"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              onClick={onToggleListening}
              disabled={disabled}
              className={`w-11 h-11 flex items-center justify-center rounded-full shadow-md active:scale-95 transition-colors ${
                isListening
                  ? 'bg-red-500 text-white animate-pulse'
                  : 'bg-stone-100 text-stone-600'
              }`}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </motion.button>
          )}
        </AnimatePresence>
      </form>
    </div>
  );
};

export { ChatInput };
