import React from 'react';

const Card = React.forwardRef(
  ({ children, noPadding = false, highlighted = false, className = '', ...props }, ref) => {
    const baseClasses = 'theme-bg-secondary rounded-card shadow-sm border theme-border transition-colors duration-200';
    const paddingClasses = noPadding ? '' : 'p-4';
    const highlightedClasses = highlighted ? 'border-l-4' : '';
    const highlightedStyle = highlighted ? { borderLeftColor: 'var(--color-accent-primary)' } : {};

    const classes = [
      baseClasses,
      paddingClasses,
      highlightedClasses,
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div ref={ref} className={classes} style={highlightedStyle} {...props}>
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

export { Card };
