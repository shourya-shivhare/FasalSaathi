import { create } from 'zustand';
import { api } from '../lib/api.jsx';
import { useUserStore } from './useUserStore.jsx';

export const useFarmStore = create((set, get) => ({
  farms: [],
  loading: false,
  error: null,

  fetchFarms: async () => {
    const token = useUserStore.getState().accessToken;
    if (!token) return;
    set({ loading: true, error: null });
    try {
      const farms = await api.getFarms(token);
      set({ farms, loading: false });
    } catch (err) {
      set({ error: err.message, loading: false });
    }
  },

  createFarm: async (data) => {
    const token = useUserStore.getState().accessToken;
    const farm = await api.createFarm(token, data);
    set((s) => ({ farms: [...s.farms, farm] }));
    return farm;
  },

  updateFarm: async (farmId, data) => {
    const token = useUserStore.getState().accessToken;
    const updated = await api.updateFarm(token, farmId, data);
    set((s) => ({
      farms: s.farms.map((f) => (f.id === farmId ? updated : f)),
    }));
    return updated;
  },

  deleteFarm: async (farmId) => {
    const token = useUserStore.getState().accessToken;
    await api.deleteFarm(token, farmId);
    set((s) => ({ farms: s.farms.filter((f) => f.id !== farmId) }));
  },
}));
