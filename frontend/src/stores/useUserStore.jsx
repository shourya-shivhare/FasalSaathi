import { create } from 'zustand';

export const useUserStore = create((set) => ({
  farmer: {
    name: 'Ramesh Kumar',
    village: 'Narela',
    state: 'Delhi',
    preferredLang: 'en',
  },
  isOnboarded: true,
  language: 'en',

  setLanguage: (lang) => {
    set((state) => ({
      language: lang,
      farmer: { ...state.farmer, preferredLang: lang },
    }));
  },

  completeOnboarding: (data) => {
    set({
      farmer: {
        name: data.name || '',
        village: data.village || '',
        state: data.state || '',
        preferredLang: data.language || 'en',
      },
      isOnboarded: true,
      language: data.language || 'en',
    });
  },

  updateFarmerProfile: (updates) => {
    set((state) => ({
      farmer: { ...state.farmer, ...updates },
    }));
  },

  resetOnboarding: () => {
    set({
      isOnboarded: false,
      farmer: {
        name: '',
        village: '',
        state: '',
        preferredLang: 'en',
      },
    });
  },
}));
