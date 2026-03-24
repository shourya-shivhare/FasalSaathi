import React from 'react';

const Card = React.forwardRef(
  ({ children, noPadding = false, highlighted = false, className = '', ...props }, ref) => {
    const baseClasses = 'bg-white rounded-card shadow-sm border border-stone-100';
    const paddingClasses = noPadding ? '' : 'p-4';
    const highlightedClasses = highlighted ? 'border-l-4 border-l-brand-500' : '';

    const classes = [
      baseClasses,
      paddingClasses,
      highlightedClasses,
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div ref={ref} className={classes} {...props}>
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

export { Card };
