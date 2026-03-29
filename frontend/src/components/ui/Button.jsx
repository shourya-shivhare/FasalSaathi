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
        'text-white focus:ring-offset-theme-bg-primary transition-all duration-200',
      secondary:
        'theme-bg-surface-hover theme-text-primary hover:opacity-80 transition-all duration-200',
      danger:
        'theme-bg-danger text-white hover:opacity-90 transition-all duration-200',
      ghost:
        'bg-transparent theme-text-primary hover:theme-bg-surface-hover transition-all duration-200',
      outline:
        'border theme-border theme-bg-secondary theme-text-primary hover:theme-bg-surface-hover transition-all duration-200',
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-xs',
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

    // Dynamic style based on theme variables
    const style =
      variant === 'primary'
        ? {
            backgroundColor: 'var(--color-accent-primary)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
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
