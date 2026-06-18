import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, api } from '../lib/api.jsx';

function mergeFarmerFromUser(prev, user) {
  if (!user) return prev;
  const fp = user.farmer_profile || {};
  return {
    ...prev,
    name: fp.full_name ?? user.name ?? prev.name,
    email: user.email ?? prev.email,
    phone: user.phone_number ?? user.phone ?? prev.phone,
    state: fp.state ?? prev.state,
    district: fp.district ?? prev.district,
    village: fp.village ?? prev.village,
    age: fp.age ?? prev.age,
    gender: fp.gender ?? prev.gender,
    land_size_acres: fp.farm_size_acres ?? fp.land_size_acres ?? prev.land_size_acres,
    crops_grown: fp.crops_grown ?? prev.crops_grown,
    category: fp.category ?? prev.category,
    annual_income: fp.annual_income ?? prev.annual_income,
    preferred_language: fp.preferred_language ?? prev.preferred_language,
    soil_type: fp.soil_type ?? prev.soil_type,
    irrigation_source: fp.irrigation_source ?? prev.irrigation_source,
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
        district: '',
        preferred_language: 'ENGLISH',
        email: '',
        phone: '',
        age: null,
        gender: '',
        land_size_acres: null,
        crops_grown: [],
        category: '',
        annual_income: null,
        soil_type: '',
        irrigation_source: '',
      },
      isOnboarded: false,
      language: 'en',

      setLanguage: (lang) => {
        set((state) => ({
          language: lang,
          farmer: { ...state.farmer, preferred_language: lang },
        }));
      },

      /** Load `/users/me` and sync farmer display fields. */
      fetchCurrentUser: async () => {
        const token = get().accessToken;
        if (!token) return null;
        try {
          const user = await authApi.getMe(token);
          const onboarded = user.farmer_profile ? user.farmer_profile.profile_completed : (user.is_onboarded || false);
          set({
            user,
            farmer: mergeFarmerFromUser(get().farmer, user),
            isOnboarded: onboarded,
          });
          return user;
        } catch (err) {
          console.error("fetchCurrentUser failed, logging out:", err);
          set({
            accessToken: null,
            user: null,
          });
          return null;
        }
      },

      setAccessToken: (token) => set({ accessToken: token }),

      // Signup Step 1: Send OTP
      signupSendOtp: async (username, phone, password, channel = 'SMS') => {
        return authApi.signupSendOtp(username, phone, password, channel);
      },

      // Signup Step 2: Verify OTP and create user
      signupVerify: async (username, phone, password, otp, deviceName = 'Web Browser', isTrusted = false) => {
        const res = await authApi.signupVerify(username, phone, password, otp, deviceName, isTrusted);
        set({
          accessToken: res.access_token,
          isOnboarded: res.profile_completed || false,
        });
        const user = await authApi.getMe(res.access_token);
        set({
          user,
          farmer: mergeFarmerFromUser(get().farmer, user),
        });
        return res;
      },

      // Login: Verify credentials and retrieve tokens directly
      login: async (username, password, deviceName = 'Web Browser', isTrusted = false) => {
        const res = await authApi.login(username, password, deviceName, isTrusted);
        set({
          accessToken: res.access_token,
          isOnboarded: res.profile_completed || false,
        });
        const user = await authApi.getMe(res.access_token);
        set({
          user,
          farmer: mergeFarmerFromUser(get().farmer, user),
        });
        return res;
      },

      completeOnboarding: async (data) => {
        const token = get().accessToken;
        // Map UI fields to backend fields
        const profileUpdates = {
          state: data.state,
          district: data.district || data.village || '',
          village: data.village || '',
          farm_size_acres: parseFloat(data.land_size_acres) || 0,
          crops_grown: data.crops_grown || [],
          age: parseInt(data.age) || null,
          gender: data.gender || '',
          preferred_language: data.preferred_language || 'ENGLISH',
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
        const mapped = { ...updates };
        if ('land_size_acres' in mapped) {
          mapped.farm_size_acres = parseFloat(mapped.land_size_acres) || 0;
        }
        if (token) {
          try {
            const updatedUser = await api.updateUserProfile(token, mapped);
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
            preferred_language: 'ENGLISH',
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

      logout: async () => {
        const token = get().accessToken;
        if (token) {
          try {
            await authApi.logout(token);
          } catch (err) {
            console.error('Logout request failed:', err);
          }
        }
        set({
          accessToken: null,
          user: null,
          isOnboarded: false,
          farmer: {
            name: '',
            village: '',
            state: '',
            district: '',
            preferred_language: 'ENGLISH',
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

      logoutAll: async () => {
        const token = get().accessToken;
        if (token) {
          try {
            await authApi.logoutAll(token);
          } catch (err) {
            console.error('Logout all request failed:', err);
          }
        }
        set({
          accessToken: null,
          user: null,
          isOnboarded: false,
          farmer: {
            name: '',
            village: '',
            state: '',
            district: '',
            preferred_language: 'ENGLISH',
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
