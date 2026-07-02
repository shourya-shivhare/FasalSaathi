import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '../lib/api';

export const useFieldStore = create(
  persist(
    (set, get) => ({
      activeFieldId: null,
      weather: null,
      soil: null,
      irrigation: null,
      fields: [], // kept as empty array for backwards compatibility stubs
      scanHistory: [], // kept as empty array for backwards compatibility stubs

      setActiveField: (id) => {
        set({ activeFieldId: id });
      },

      updateSensorData: (data) => {
        // No-op stub
      },

      fetchWeather: async (location) => {
        set({ isWeatherLoading: true });

        try {
          const lat = location?.lat || 28.6139;
          const lng = location?.lng || location?.lon || 77.209;

          const weatherData = await api.getWeather({ lat, lon: lng });
          
          set({
            weather: weatherData,
            isWeatherLoading: false,
          });
        } catch (error) {
          console.error('Failed to fetch weather:', error);
          set({
            weather: { temp: '--', humidity: '--', windSpeed: '--', condition: 'Unavailable', riskLevel: 'LOW', lastUpdated: new Date() },
            isWeatherLoading: false,
          });
        }
      },

      addField: (fieldData) => {
        // No-op stub for backwards compatibility
        return { id: `stub-${Date.now()}` };
      },

      addScanRecord: (record) => {
        // No-op stub
      },

      updateField: (id, updates) => {
        // No-op stub
      },

      deleteField: (id) => {
        // No-op stub
      },

      getActiveField: () => {
        // No-op stub
        return null;
      },

      getTotalLand: () => 0,
      getUniqueCrops: () => [],
    }),
    {
      name: 'fasalsaathi-fields-v2', // Changed storage key to avoid cache pollution from older schema versions
      partialize: (s) => ({
        activeFieldId: s.activeFieldId,
      }),
    }
  )
);
