import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MoreVertical,
  Phone,
  Search,
  Wifi,
  WifiOff,
  Loader2,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronUp,
  Moon,
  Sun,
} from 'lucide-react';
import { useThemeStore } from '../../../stores/useThemeStore.jsx';

// ─── Chat Header ──────────────────────────────────────────────────────────────
export const ChatHeader = ({ isThinking }) => {
  const { theme, toggleTheme } = useThemeStore();
  const isDark = theme === 'dark';

  return (
    <div
      className="fixed top-0 left-0 right-0 z-30 px-4 py-3 flex items-center gap-3 transition-colors duration-300"
      style={{
        background: isDark ? 'var(--color-bg-secondary)' : 'var(--color-accent-primary)',
        boxShadow: isDark ? '0 2px 8px rgba(0,0,0,0.5)' : '0 2px 8px rgba(74,124,63,0.3)',
      }}
    >
      {/* Avatar */}
      <div
        className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
        style={{ 
          background: isDark ? 'var(--color-surface-hover)' : 'rgba(255,255,255,0.2)', 
          border: isDark ? '1px solid var(--color-border)' : '2px solid rgba(255,255,255,0.4)' 
        }}
      >
        FS
      </div>

      {/* Name + status */}
      <div className="flex-1 min-w-0">
        <h1 
          className="font-semibold text-base leading-tight transition-colors"
          style={{ color: isDark ? 'var(--color-text-primary)' : '#ffffff' }}
        >
          FasalSaathi
        </h1>
        <AnimatePresence mode="wait">
          {isThinking ? (
            <motion.p
              key="thinking"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-xs flex items-center gap-1 transition-colors"
              style={{ color: isDark ? 'var(--color-accent-primary)' : 'rgba(255,255,255,0.8)' }}
            >
              <Loader2 className="w-3 h-3 animate-spin" />
              typing…
            </motion.p>
          ) : (
            <motion.p
              key="online"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-xs transition-colors"
              style={{ color: isDark ? 'var(--color-text-secondary)' : 'rgba(255,255,255,0.8)' }}
            >
              online
            </motion.p>
          )}
        </AnimatePresence>
      </div>

      {/* Action icons */}
      <div className="flex items-center gap-1">
        <button 
          onClick={toggleTheme}
          className="p-2 transition-colors hover:bg-white/10 rounded-lg"
          style={{ color: isDark ? 'var(--color-text-primary)' : '#ffffff' }}
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        <button className="p-2 transition-colors hover:bg-white/10 rounded-lg" style={{ color: isDark ? 'var(--color-text-primary)' : '#ffffff' }}>
          <Search className="w-5 h-5" />
        </button>
        <button className="p-2 transition-colors hover:bg-white/10 rounded-lg" style={{ color: isDark ? 'var(--color-text-primary)' : '#ffffff' }}>
          <MoreVertical className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

// ─── Agent Thinking Accordion ─────────────────────────────────────────────────
const stepIcon = (status) => {
  if (status === 'done')  return <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />;
  if (status === 'error') return <XCircle className="w-3.5 h-3.5 text-red-500" />;
  return <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-500" />;
};

export const AgentThinkingAccordion = ({ agentSteps, isThinking }) => {
  const [open, setOpen] = React.useState(true);
  if (!isThinking) return null;

  return (
    <div
      className="mx-3 mb-1 rounded-xl overflow-hidden shadow-sm transition-colors duration-300"
      style={{ 
        background: 'var(--color-bg-secondary)', 
        border: '1px solid var(--color-border)' 
      }}
    >
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3 py-2"
      >
        <span 
          className="flex items-center gap-1.5 text-xs font-semibold"
          style={{ color: 'var(--color-accent-secondary)' }}
        >
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          Thinking…
        </span>
        <ChevronUp 
          className={`w-4 h-4 transition-transform ${!open ? 'rotate-180' : ''}`} 
          style={{ color: 'var(--color-text-secondary)' }}
        />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-2 space-y-1.5">
              {agentSteps.map((step, i) => (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-center gap-2"
                >
                  {stepIcon(step.status)}
                  <span className="text-xs font-medium" style={{ color: 'var(--color-text-primary)' }}>{step.label}</span>
                  {step.detail && (
                    <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>— {step.detail}</span>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
