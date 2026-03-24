import React, { useEffect } from 'react';
import { CheckCircle, AlertCircle, XCircle, Info, X } from 'lucide-react';

const Toast = React.forwardRef(
  ({ message, type = 'info', isOpen, onClose, duration = 5000, className = '' }, ref) => {
    useEffect(() => {
      if (isOpen && duration > 0) {
        const timer = setTimeout(onClose, duration);
        return () => clearTimeout(timer);
      }
    }, [isOpen, duration, onClose]);

    if (!isOpen) return null;

    const typeConfig = {
      success: {
        icon: CheckCircle,
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        textColor: 'text-green-800',
        iconColor: 'text-green-500',
      },
      warning: {
        icon: AlertCircle,
        bgColor: 'bg-amber-50',
        borderColor: 'border-amber-200',
        textColor: 'text-amber-800',
        iconColor: 'text-amber-500',
      },
      error: {
        icon: XCircle,
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        textColor: 'text-red-800',
        iconColor: 'text-red-500',
      },
      info: {
        icon: Info,
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        textColor: 'text-blue-800',
        iconColor: 'text-blue-500',
      },
    };

    const config = typeConfig[type] || typeConfig.info;
    const Icon = config.icon;

    return (
      <div
        ref={ref}
        className={`fixed top-4 right-4 z-50 flex items-center gap-3 p-4 rounded-lg border ${config.bgColor} ${config.borderColor} ${config.textColor} shadow-lg max-w-sm animate-pulse ${className}`}
      >
        <Icon className={`w-5 h-5 flex-shrink-0 ${config.iconColor}`} />
        <p className="text-sm font-medium">{message}</p>
        <button
          onClick={onClose}
          className={`ml-auto flex-shrink-0 ${config.iconColor} hover:opacity-75 transition-opacity`}
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }
);

Toast.displayName = 'Toast';

export { Toast };
