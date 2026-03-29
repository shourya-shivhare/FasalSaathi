import React from 'react';

const ProgressBar = ({ value = 0, colorScheme = 'auto', className = '' }) => {
  const getColorClass = () => {
    if (colorScheme === 'auto') {
      if (value >= 60) return 'theme-bg-success';
      if (value >= 30) return 'theme-bg-warning';
      return 'theme-bg-danger';
    }

    const schemeClasses = {
      green: 'theme-bg-success',
      amber: 'theme-bg-warning',
      red: 'theme-bg-danger',
    };

    return schemeClasses[colorScheme] || 'theme-bg-accent-primary';
  };

  return (
    <div className={`w-full theme-bg-surface-hover rounded-full h-2 transition-colors duration-200 ${className}`}>
      <div
        className={`${getColorClass()} h-2 rounded-full transition-all duration-500 ease-out`}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
};

export { ProgressBar };
