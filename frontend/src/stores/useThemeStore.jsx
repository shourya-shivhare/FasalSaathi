import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useThemeStore = create()(
  persist(
    (set, get) => ({
      theme: 'light', // default

      // Initialize theme on store load
      initTheme: () => {
        const saved = localStorage.getItem('theme-storage');
        if (saved) {
          try {
            const parsed = JSON.parse(saved);
            const theme = parsed.state.theme;
            document.documentElement.setAttribute('data-theme', theme);
          } catch (e) {
            console.error('Failed to parse theme storage', e);
          }
        } else {
          // Check system preference if no saved theme
          const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          const initial = systemDark ? 'dark' : 'light';
          set({ theme: initial });
          document.documentElement.setAttribute('data-theme', initial);
        }
      },

      toggleTheme: () => {
        const current = get().theme;
        const nextTheme = current === 'light' ? 'dark' : 'light';
        set({ theme: nextTheme });
        document.documentElement.setAttribute('data-theme', nextTheme);
      },
    }),
    {
      name: 'theme-storage',
    }
  )
);

export { useThemeStore };
