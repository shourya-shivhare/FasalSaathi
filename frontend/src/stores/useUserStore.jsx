import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, api } from '../lib/api.jsx';

function mergeFarmerFromUser(prev, user) {
  if (!user) return prev;
  return {
    ...prev,
    name: user.name ?? prev.name,
    email: user.email ?? prev.email,
    phone: user.phone ?? prev.phone,
    state: user.state ?? prev.state,
    district: user.district ?? prev.district,
    age: user.age ?? prev.age,
    gender: user.gender ?? prev.gender,
    land_size_acres: user.land_size_acres ?? prev.land_size_acres,
    crops_grown: user.crops_grown ?? prev.crops_grown,
    category: user.category ?? prev.category,
    annual_income: user.annual_income ?? prev.annual_income,
  };
}

export const useUserStore = create(
  persist(
    (set, get) => ({
      accessToken: null,
      user: null,
      farmer: {
        name: '',
        village: '', // maps to district or town in UI
        state: '',
        district: '',
        preferredLang: 'en',
        email: '',
        phone: '',
        age: null,
        gender: '',
        land_size_acres: null,
        crops_grown: [],
        category: '',
        annual_income: null,
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

      completeOnboarding: async (data) => {
        const token = get().accessToken;
        // Map UI fields to backend fields
        const profileUpdates = {
          state: data.state,
          district: data.village || data.district,
          land_size_acres: parseFloat(data.land_size_acres) || 0,
          crops_grown: data.crops_grown || [],
          age: parseInt(data.age) || null,
          gender: data.gender || '',
        };

        if (token) {
          try {
            const updatedUser = await api.updateUserProfile(token, profileUpdates);
            set({
              user: updatedUser,
              farmer: mergeFarmerFromUser(get().farmer, updatedUser),
              isOnboarded: true,
              language: data.language || get().language,
            });
          } catch (err) {
            console.error('Failed to sync profile to backend:', err);
            // Still mark as onboarded locally to allow access
            set({ isOnboarded: true });
          }
        } else {
          set({ isOnboarded: true });
        }
      },

      updateFarmerProfile: async (updates) => {
        const token = get().accessToken;
        if (token) {
          try {
            const updatedUser = await api.updateUserProfile(token, updates);
            set({
              user: updatedUser,
              farmer: mergeFarmerFromUser(get().farmer, updatedUser),
            });
            return updatedUser;
          } catch (err) {
            console.error('Update failed:', err);
            throw err;
          }
        } else {
          set((state) => ({
            farmer: { ...state.farmer, ...updates },
          }));
        }
      },

      resetOnboarding: () => {
        set({
          isOnboarded: false,
          farmer: {
            name: '',
            village: '',
            state: '',
            district: '',
            preferredLang: 'en',
            email: '',
            phone: '',
            age: null,
            gender: '',
            land_size_acres: null,
            crops_grown: [],
            category: '',
            annual_income: null,
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
            district: '',
            preferredLang: 'en',
            email: '',
            phone: '',
            age: null,
            gender: '',
            land_size_acres: null,
            crops_grown: [],
            category: '',
            annual_income: null,
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
