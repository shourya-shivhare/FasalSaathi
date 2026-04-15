// src/stores/useResultsStore.jsx
// Persisted store for crop and scheme recommendation results.
// Survives page navigation and browser refresh via localStorage.
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useResultsStore = create(
  persist(
    (set) => ({
      // ── Crop Suggestion Results ──────────────────────────────────────────
      cropResults: {
        crops: [],
        summary: '',
        pestNote: '',
        hasSearched: false,
      },

      setCropResults: ({ crops, summary, pestNote }) =>
        set({
          cropResults: { crops, summary, pestNote, hasSearched: true },
        }),

      clearCropResults: () =>
        set({
          cropResults: { crops: [], summary: '', pestNote: '', hasSearched: false },
        }),

      // ── Scheme Results ───────────────────────────────────────────────────
      schemeResults: {
        schemes: [],
        summary: '',
        totalFound: 0,
        hasSearched: false,
      },

      setSchemeResults: ({ schemes, summary, totalFound }) =>
        set({
          schemeResults: { schemes, summary, totalFound, hasSearched: true },
        }),

      clearSchemeResults: () =>
        set({
          schemeResults: { schemes: [], summary: '', totalFound: 0, hasSearched: false },
        }),
    }),
    {
      name: 'fasalsaathi-results',
    }
  )
);
