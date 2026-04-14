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
              className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-all duration-300"
              onClick={onClose}
            />

            {/* Panel */}
            <motion.div
              ref={ref}
              initial={{ opacity: 0, scale: 0.95, y: 16 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 16 }}
              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
              className={`relative w-full ${sizeClasses[size]} rounded-2xl overflow-hidden shadow-2xl theme-bg-primary border theme-border transition-all duration-300 ${className}`}
            >
              {/* Title header (only for modals that pass title — AddFieldForm brings its own) */}
              {title && (
                <div
                  className="flex items-center justify-between px-5 py-4 theme-bg-accent-primary transition-colors duration-200"
                >
                  <h2 className="theme-text-on-accent font-bold text-base">{title}</h2>
                  {onClose && (
                    <button
                      onClick={onClose}
                      className="p-1 rounded-lg theme-text-on-accent opacity-60 hover:opacity-100 hover:bg-white/10 transition-all"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </div>
              )}

              {/* Content */}
              <div className="theme-text-primary transition-colors duration-200">{children}</div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    );
  }
);

Modal.displayName = 'Modal';

export { Modal };
