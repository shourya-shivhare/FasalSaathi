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
    const baseClasses = 'font-semibold rounded-button transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 min-h-[48px] flex items-center justify-center gap-2';
    
    const variantClasses = {
      primary: 'bg-brand-600 hover:bg-brand-700 text-white focus:ring-brand-500',
      secondary: 'bg-earth-200 hover:bg-earth-300 text-earth-900 focus:ring-earth-500',
      danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
      ghost: 'bg-transparent hover:bg-earth-100 text-earth-700 focus:ring-earth-500',
      outline: 'border border-earth-300 bg-transparent hover:bg-earth-50 text-earth-700 focus:ring-earth-500',
    };

    const sizeClasses = {
      sm: 'px-3 py-2 text-sm',
      md: 'px-4 py-3 text-base',
      lg: 'px-6 py-4 text-lg',
    };

    const classes = [
      baseClasses,
      variantClasses[variant],
      sizeClasses[size],
      fullWidth && 'w-full',
      (disabled || loading) && 'opacity-50 cursor-not-allowed',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || loading}
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
