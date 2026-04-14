import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useFieldStore = create(
  persist(
    (set, get) => ({
      fields: [],
      activeFieldId: null,
      weather: null,
      soil: null,
      irrigation: null,
      scanHistory: [], // track pest scans

      setActiveField: (id) => {
        set({ activeFieldId: id });
        // Update soil data from the selected field
        const field = get().fields.find((f) => f.id === id);
        if (field?.soilHealth) {
          set({
            soil: {
              N: field.soilHealth.N,
              P: field.soilHealth.P,
              K: field.soilHealth.K,
              pH: field.soilHealth.pH,
              moisture: field.sensors?.moisture || 60,
            },
          });
        }
      },

      updateSensorData: (data) => {
        set((state) => {
          if (!state.activeFieldId) return state;

          return {
            fields: state.fields.map((field) =>
              field.id === state.activeFieldId
                ? { ...field, sensors: { ...field.sensors, ...data } }
                : field
            ),
          };
        });
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
          // Set a sensible fallback so the UI doesn't break
          set({
            weather: { temp: '--', humidity: '--', windSpeed: '--', condition: 'Unavailable', riskLevel: 'LOW', lastUpdated: new Date() },
            isWeatherLoading: false,
          });
        }
      },

      addField: (fieldData) => {
        const newField = {
          id: `field-${Date.now()}`,
          ...fieldData,
          sensors: { moisture: 60, temperature: 25, ph: 6.5 },
          growthStage: fieldData.growthStage || 'Sowing',
          soilHealth: fieldData.soilHealth || { score: 75, N: 280, P: 25, K: 200, pH: 6.5 },
          createdAt: new Date().toISOString(),
        };

        set((state) => ({
          fields: [...state.fields, newField],
          // Auto-select as active if it's the first field
          activeFieldId: state.activeFieldId || newField.id,
          // Also set soil from this field if it's the first
          soil: state.soil || {
            N: newField.soilHealth.N,
            P: newField.soilHealth.P,
            K: newField.soilHealth.K,
            pH: newField.soilHealth.pH,
            moisture: 60,
          },
        }));

        return newField;
      },

      addScanRecord: (record) => {
        set((state) => ({
          scanHistory: [
            { id: `scan-${Date.now()}`, timestamp: new Date().toISOString(), ...record },
            ...state.scanHistory,
          ].slice(0, 50), // Keep last 50
        }));
      },

      updateField: (id, updates) => {
        set((state) => ({
          fields: state.fields.map((field) =>
            field.id === id ? { ...field, ...updates } : field
          ),
        }));
      },

      deleteField: (id) => {
        set((state) => ({
          fields: state.fields.filter((field) => field.id !== id),
          activeFieldId: state.activeFieldId === id ? (state.fields[0]?.id || null) : state.activeFieldId,
        }));
      },

      getActiveField: () => {
        const { fields, activeFieldId } = get();
        return fields.find((field) => field.id === activeFieldId) || null;
      },

      getTotalLand: () => {
        return get().fields.reduce((sum, f) => sum + (parseFloat(f.area) || 0), 0);
      },

      getUniqueCrops: () => {
        const crops = get().fields.map((f) => f.crop).filter(Boolean);
        return [...new Set(crops)];
      },
    }),
    {
      name: 'fasalsaathi-fields',
      partialize: (s) => ({
        fields: s.fields,
        activeFieldId: s.activeFieldId,
        scanHistory: s.scanHistory,
      }),
    }
  )
);
