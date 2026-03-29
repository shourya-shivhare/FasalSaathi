import React from 'react';

/**
 * Standard page shell used by all non-chat pages.
 * Accounts for:
 *   - fixed top bar  : 60px
 *   - fixed bottom nav: 64px
 */
const PageWrapper = ({ children, className = '' }) => (
  <div
    className={`min-h-dvh overflow-y-auto transition-colors duration-300 ${className}`}
    style={{
      position: 'relative',
      zIndex: 0,
      background: 'var(--color-bg-primary)',
      paddingTop: '60px',
      paddingBottom: '64px',
    }}
  >
    {children}
  </div>
);

export { PageWrapper };
