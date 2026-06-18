import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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
          // Use Open-Meteo (free, no API key needed)
          const lat = location?.lat || 28.6139;
          const lng = location?.lng || location?.lon || 77.209;

          const res = await fetch(
            `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}` +
            `&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code` +
            `&forecast_days=1`
          );
          const data = await res.json();

          if (data?.current) {
            const temp = Math.round(data.current.temperature_2m);
            const humidity = data.current.relative_humidity_2m;
            const windSpeed = Math.round(data.current.wind_speed_10m);

            const codeMap = {
              0: 'Sunny', 1: 'Mostly Clear', 2: 'Partly Cloudy', 3: 'Cloudy',
              45: 'Foggy', 48: 'Foggy', 51: 'Drizzle', 53: 'Drizzle',
              61: 'Rainy', 63: 'Rainy', 65: 'Heavy Rain',
              71: 'Snow', 80: 'Showers', 95: 'Thunderstorm',
            };
            const condition = codeMap[data.current.weather_code] || 'Clear';

            const riskLevel = temp > 40 ? 'HIGH' : temp > 35 ? 'MODERATE' : humidity > 85 ? 'MODERATE' : 'LOW';

            set({
              weather: { temp, humidity, windSpeed, condition, riskLevel, lastUpdated: new Date() },
              isWeatherLoading: false,
            });
          } else {
            set({ isWeatherLoading: false });
          }
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
