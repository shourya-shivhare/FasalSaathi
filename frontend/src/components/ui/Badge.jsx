import React from 'react';

const Badge = React.forwardRef(
  ({ children, variant = 'neutral', className = '', ...props }, ref) => {
    const baseClasses = 'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium';
    
    const variantClasses = {
      success: 'theme-bg-success theme-text-on-success transition-colors duration-200',
      warning: 'theme-bg-warning theme-text-on-warning transition-colors duration-200',
      danger: 'theme-bg-danger theme-text-on-danger transition-colors duration-200',
      info: 'theme-bg-accent-secondary text-black transition-colors duration-200',
      neutral: 'theme-bg-surface-hover theme-text-secondary transition-colors duration-200 border theme-border',
    };

    const classes = [
      baseClasses,
      variantClasses[variant],
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <span ref={ref} className={classes} {...props}>
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

export { Badge };
