import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

const Modal = React.forwardRef(
  ({ isOpen, onClose, title, children, size = 'md', className = '' }, ref) => {
    const sizeClasses = {
      sm: 'max-w-sm',
      md: 'max-w-lg',
      lg: 'max-w-2xl',
      xl: 'max-w-4xl',
    };

    return (
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0"
              style={{ background: 'rgba(0,0,0,0.45)', backdropFilter: 'blur(4px)' }}
              onClick={onClose}
            />

            {/* Panel */}
            <motion.div
              ref={ref}
              initial={{ opacity: 0, scale: 0.95, y: 16 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 16 }}
              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
              className={`relative w-full ${sizeClasses[size]} rounded-2xl overflow-hidden shadow-2xl ${className}`}
              style={{
                background: '#f0fdf4',
                border: '1px solid #bbf7d0',
              }}
            >
              {/* Title header (only for modals that pass title — AddFieldForm brings its own) */}
              {title && (
                <div
                  className="flex items-center justify-between px-5 py-4"
                  style={{
                    background: 'linear-gradient(135deg, #16a34a, #15803d)',
                  }}
                >
                  <h2 className="text-white font-bold text-base">{title}</h2>
                  {onClose && (
                    <button
                      onClick={onClose}
                      className="p-1 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-all"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </div>
              )}

              {/* Content */}
              <div>{children}</div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    );
  }
);

Modal.displayName = 'Modal';

export { Modal };
