// src/stores/useResultsStore.jsx
// In-memory store for crop and scheme recommendation results.
// Survives SPA page navigation but clears on browser refresh.
import { create } from 'zustand';

export const useResultsStore = create(
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
  })
);
