import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { Card } from '../../../components/ui/Card';

const AgentThinkingAccordion = ({ agentSteps, isThinking }) => {
  const [isExpanded, setIsExpanded] = React.useState(true);

  if (!isThinking) return null;

  const getStepIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Loader2 className="w-4 h-4 animate-spin text-stone-400" />;
      case 'done':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Loader2 className="w-4 h-4 animate-spin text-stone-400" />;
    }
  };

  return (
    <Card className="border-l-4 border-l-amber-500 bg-amber-50">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 text-left"
      >
        <div className="flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
          <span className="text-sm font-medium text-amber-800">
            FasalSaathi is thinking...
          </span>
        </div>
        
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-amber-600" />
        ) : (
          <ChevronDown className="w-4 h-4 text-amber-600" />
        )}
      </button>
      
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 space-y-2">
              {agentSteps.map((step, index) => (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.15 }}
                  className="flex items-center gap-3 py-2"
                >
                  {getStepIcon(step.status)}
                  <div className="flex-1">
                    <div className="text-sm font-medium text-stone-700">
                      {step.label}
                    </div>
                    {step.detail && (
                      <div className="text-xs text-stone-500">
                        {step.detail}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

export { AgentThinkingAccordion };
