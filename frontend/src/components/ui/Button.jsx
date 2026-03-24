import React from 'react';
import { Loader2 } from 'lucide-react';

const Button = React.forwardRef(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      loading = false,
      disabled = false,
      fullWidth = false,
      icon: Icon,
      className = '',
      ...props
    },
    ref
  ) => {
    const base =
      'font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 min-h-[44px] flex items-center justify-center gap-2 active:scale-[0.97]';

    const variants = {
      primary:
        'text-white focus:ring-green-400 shadow-md',
      secondary:
        'bg-green-50 hover:bg-green-100 text-green-700 focus:ring-green-400',
      danger:
        'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
      ghost:
        'bg-transparent hover:bg-green-50 text-green-700 focus:ring-green-400',
      outline:
        'border border-green-300 bg-white hover:bg-green-50 text-green-700 focus:ring-green-400',
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2.5 text-sm',
      lg: 'px-6 py-3.5 text-base',
    };

    const cls = [
      base,
      variants[variant],
      sizes[size],
      fullWidth && 'w-full',
      (disabled || loading) && 'opacity-50 cursor-not-allowed',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    // Gradient style only for primary
    const style =
      variant === 'primary'
        ? {
            background: 'linear-gradient(135deg, #16a34a, #15803d)',
            boxShadow: '0 2px 8px rgba(22,163,74,0.3)',
          }
        : undefined;

    return (
      <button
        ref={ref}
        className={cls}
        disabled={disabled || loading}
        style={style}
        {...props}
      >
        {loading && <Loader2 className="w-4 h-4 animate-spin" />}
        {Icon && !loading && <Icon className="w-4 h-4" />}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
