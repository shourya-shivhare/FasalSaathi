import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../lib/api.jsx';

function mergeFarmerFromUser(prev, user) {
  if (!user) return prev;
  return {
    ...prev,
    name: user.name ?? prev.name,
    email: user.email ?? prev.email,
    phone: user.phone ?? prev.phone,
  };
}

export const useUserStore = create(
  persist(
    (set, get) => ({
      accessToken: null,
      user: null,
      farmer: {
        name: '',
        village: '',
        state: '',
        preferredLang: 'en',
        email: '',
        phone: '',
      },
      isOnboarded: false,
      language: 'en',

      setLanguage: (lang) => {
        set((state) => ({
          language: lang,
          farmer: { ...state.farmer, preferredLang: lang },
        }));
      },

      /** Load `/users/me` and sync farmer display fields. */
      fetchCurrentUser: async () => {
        const token = get().accessToken;
        if (!token) return null;
        try {
          const user = await authApi.getMe(token);
          set({
            user,
            farmer: mergeFarmerFromUser(get().farmer, user),
          });
          return user;
        } catch {
          set({
            accessToken: null,
            user: null,
          });
          return null;
        }
      },

      setAccessToken: (token) => set({ accessToken: token }),

      login: async (email, password) => {
        const { access_token: accessToken } = await authApi.login(email, password);
        set({ accessToken });
        const user = await authApi.getMe(accessToken);
        set({
          user,
          farmer: mergeFarmerFromUser(get().farmer, user),
        });
      },

      register: async ({ name, email, password, phone }) => {
        const { access_token: accessToken } = await authApi.register({
          name,
          email,
          password,
          phone,
        });
        set({ accessToken });
        const user = await authApi.getMe(accessToken);
        set({
          user,
          farmer: mergeFarmerFromUser(get().farmer, user),
          isOnboarded: false,
        });
      },

      completeOnboarding: (data) => {
        set({
          farmer: {
            ...get().farmer,
            name: data.name || get().farmer.name,
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
            email: '',
            phone: '',
          },
        });
      },

      logout: () => {
        set({
          accessToken: null,
          user: null,
          isOnboarded: false,
          farmer: {
            name: '',
            village: '',
            state: '',
            preferredLang: 'en',
            email: '',
            phone: '',
          },
        });
      },
    }),
    {
      name: 'fasalsaathi-user',
      partialize: (s) => ({
        accessToken: s.accessToken,
        user: s.user,
        farmer: s.farmer,
        isOnboarded: s.isOnboarded,
        language: s.language,
      }),
    }
  )
);
