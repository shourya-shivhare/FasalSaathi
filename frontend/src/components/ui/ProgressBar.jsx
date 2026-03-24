import React from 'react';

const ProgressBar = ({ value = 0, colorScheme = 'auto', className = '' }) => {
  const getColorClass = () => {
    if (colorScheme === 'auto') {
      if (value >= 60) return 'bg-green-500';
      if (value >= 30) return 'bg-amber-500';
      return 'bg-red-500';
    }

    const schemeClasses = {
      green: 'bg-green-500',
      amber: 'bg-amber-500',
      red: 'bg-red-500',
    };

    return schemeClasses[colorScheme] || 'bg-green-500';
  };

  return (
    <div className={`w-full bg-stone-200 rounded-full h-2 ${className}`}>
      <div
        className={`${getColorClass()} h-2 rounded-full transition-all duration-500 ease-out`}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
};

export { ProgressBar };
