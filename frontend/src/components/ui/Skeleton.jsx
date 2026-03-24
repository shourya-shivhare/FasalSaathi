import React from 'react';

const Skeleton = ({ variant = 'text', width, height, className = '' }) => {
  const baseClasses = 'shimmer';
  
  const variantClasses = {
    text: 'h-4 w-full rounded',
    circle: 'rounded-full',
    rectangle: 'rounded',
  };

  const styleClasses = {
    width: width || (variant === 'circle' ? '40px' : undefined),
    height: height || (variant === 'circle' ? '40px' : undefined),
  };

  const classes = [
    baseClasses,
    variantClasses[variant],
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div
      className={classes}
      style={styleClasses}
    />
  );
};

export { Skeleton };
