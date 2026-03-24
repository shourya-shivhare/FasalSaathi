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
} from 'lucide-react';

// ─── Chat Header ──────────────────────────────────────────────────────────────
export const ChatHeader = ({ isThinking }) => (
  <div
    className="fixed top-0 left-0 right-0 z-30 px-4 py-3 flex items-center gap-3"
    style={{
      background: 'linear-gradient(135deg, #16a34a, #15803d)',
      boxShadow: '0 2px 8px rgba(22,163,74,0.3)',
    }}
  >
    {/* Avatar */}
    <div
      className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
      style={{ background: 'rgba(255,255,255,0.2)', border: '2px solid rgba(255,255,255,0.4)' }}
    >
      FS
    </div>

    {/* Name + status */}
    <div className="flex-1 min-w-0">
      <h1 className="text-white font-semibold text-base leading-tight">FasalSaathi</h1>
      <AnimatePresence mode="wait">
        {isThinking ? (
          <motion.p
            key="thinking"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-green-200 text-xs flex items-center gap-1"
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
            className="text-green-200 text-xs"
          >
            online
          </motion.p>
        )}
      </AnimatePresence>
    </div>

    {/* Action icons */}
    <div className="flex items-center gap-1">
      <button className="p-2 text-white/80 hover:text-white transition-colors">
        <Search className="w-5 h-5" />
      </button>
      <button className="p-2 text-white/80 hover:text-white transition-colors">
        <Phone className="w-5 h-5" />
      </button>
      <button className="p-2 text-white/80 hover:text-white transition-colors">
        <MoreVertical className="w-5 h-5" />
      </button>
    </div>
  </div>
);

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
      className="mx-3 mb-1 rounded-xl overflow-hidden shadow-sm"
      style={{ background: '#fffbeb', border: '1px solid #fde68a' }}
    >
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3 py-2"
      >
        <span className="flex items-center gap-1.5 text-xs font-semibold text-amber-700">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          Thinking…
        </span>
        {open ? (
          <ChevronUp className="w-4 h-4 text-amber-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-amber-500" />
        )}
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
                  <span className="text-xs text-stone-700 font-medium">{step.label}</span>
                  {step.detail && (
                    <span className="text-xs text-stone-400">— {step.detail}</span>
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
