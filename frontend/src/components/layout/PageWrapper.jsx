import React from 'react';

const PageWrapper = ({ children, className = '' }) => {
  return (
    <div className={`min-h-screen bg-stone-50 pb-20 ${className}`}>
      {children}
    </div>
  );
};

export { PageWrapper };
