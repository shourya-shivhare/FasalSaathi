import React from 'react';

/**
 * Standard page shell used by all non-Home pages.
 * Works with the fixed left sidebar layout — no top/bottom bar offsets.
 */
const PageWrapper = ({ children, className = '' }) => (
  <div
    className={`min-h-dvh overflow-y-auto transition-colors duration-300 ${className}`}
    style={{
      position: 'relative',
      zIndex: 0,
      background: 'var(--color-bg-primary)',
      padding: '32px',
    }}
  >
    {children}
  </div>
);

export { PageWrapper };

