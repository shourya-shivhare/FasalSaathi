import React from 'react';
import { X } from 'lucide-react';

const Modal = React.forwardRef(
  ({ isOpen, onClose, title, children, size = 'md', className = '' }, ref) => {
    if (!isOpen) return null;

    const sizeClasses = {
      sm: 'max-w-sm',
      md: 'max-w-lg',
      lg: 'max-w-2xl',
      xl: 'max-w-4xl',
    };

    return (
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex min-h-screen items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
            onClick={onClose}
          />
          
          {/* Modal */}
          <div
            ref={ref}
            className={`relative w-full ${sizeClasses[size]} bg-white rounded-card shadow-xl ${className}`}
          >
            {/* Header */}
            {(title || onClose) && (
              <div className="flex items-center justify-between p-6 border-b border-stone-200">
                {title && (
                  <h2 className="text-xl font-semibold text-stone-900">
                    {title}
                  </h2>
                )}
                {onClose && (
                  <button
                    onClick={onClose}
                    className="p-2 text-stone-400 hover:text-stone-600 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            )}
            
            {/* Content */}
            <div className="p-6">
              {children}
            </div>
          </div>
        </div>
      </div>
    );
  }
);

Modal.displayName = 'Modal';

export { Modal };
