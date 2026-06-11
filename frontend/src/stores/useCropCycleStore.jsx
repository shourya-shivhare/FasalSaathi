import { create } from 'zustand';
import { api } from '../lib/api.jsx';
import { useUserStore } from './useUserStore.jsx';

export const useCropCycleStore = create((set, get) => ({
  cycles: [],
  loading: false,
  error: null,

  fetchCycles: async (params = {}) => {
    const token = useUserStore.getState().accessToken;
    if (!token) return;
    set({ loading: true, error: null });
    try {
      const cycles = await api.getCropCycles(token, params);
      set({ cycles, loading: false });
    } catch (err) {
      set({ error: err.message, loading: false });
    }
  },

  createCycle: async (data) => {
    const token = useUserStore.getState().accessToken;
    const cycle = await api.createCropCycle(token, data);
    set((s) => ({ cycles: [cycle, ...s.cycles] }));
    return cycle;
  },

  updateCycle: async (cycleId, data) => {
    const token = useUserStore.getState().accessToken;
    const updated = await api.updateCropCycle(token, cycleId, data);
    set((s) => ({
      cycles: s.cycles.map((c) => (c.id === cycleId ? updated : c)),
    }));
    return updated;
  },

  updateStage: async (cycleId, stage) => {
    const token = useUserStore.getState().accessToken;
    const updated = await api.updateCropStage(token, cycleId, stage);
    set((s) => ({
      cycles: s.cycles.map((c) => (c.id === cycleId ? updated : c)),
    }));
    return updated;
  },

  completeCycle: async (cycleId) => {
    const token = useUserStore.getState().accessToken;
    const updated = await api.completeCropCycle(token, cycleId);
    set((s) => ({
      cycles: s.cycles.map((c) => (c.id === cycleId ? updated : c)),
    }));
    return updated;
  },
}));
