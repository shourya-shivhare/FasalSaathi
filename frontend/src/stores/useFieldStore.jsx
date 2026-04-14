import { create } from 'zustand';
import { mockFields, mockWeather, mockSoil, mockIrrigation } from '../lib/mockData';

export const useFieldStore = create((set, get) => ({
  fields: mockFields,
  activeFieldId: mockFields[0]?.id || null,
  weather: mockWeather,
  soil: mockSoil,
  irrigation: mockIrrigation,

  setActiveField: (id) => {
    set({ activeFieldId: id });
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
    const API_KEY = import.meta.env.VITE_WEATHER_API_KEY;
    if (!API_KEY) return;

    set({ isWeatherLoading: true });
    
    try {
      let url = '';
      if (location.lat && location.lng) {
        url = `https://api.openweathermap.org/data/2.5/weather?lat=${location.lat}&lon=${location.lng}&appid=${API_KEY}&units=metric`;
      } else {
        const query = location.village || location.name || 'Delhi';
        url = `https://api.openweathermap.org/data/2.5/weather?q=${query}&appid=${API_KEY}&units=metric`;
      }

      const response = await fetch(url);
      const data = await response.json();

      if (response.ok) {
        const riskLevel = data.main.temp > 35 ? 'HIGH' : data.main.temp > 30 ? 'MODERATE' : 'LOW';
        
        const updatedWeather = {
          temp: Math.round(data.main.temp),
          condition: data.weather[0].main,
          humidity: data.main.humidity,
          windSpeed: Math.round(data.wind.speed * 3.6), // Convert m/s to km/h
          riskLevel: riskLevel,
          lastUpdated: new Date(),
        };

        set({ weather: updatedWeather, isWeatherLoading: false });
      } else {
        console.error('Weather API Error:', data.message);
        set({ isWeatherLoading: false });
      }
    } catch (error) {
      console.error('Failed to fetch weather:', error);
      set({ isWeatherLoading: false });
    }
  },

  addField: (fieldData) => {
    const newField = {
      id: `field-${Date.now()}`,
      ...fieldData,
      sensors: { moisture: 60, temperature: 25, ph: 6.5 },
      growthStage: 'Sowing',
      soilHealth: { score: 75, N: 280, P: 25, K: 200, pH: 6.5 },
    };

    set((state) => ({
      fields: [...state.fields, newField],
    }));

    return newField;
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
      activeFieldId: state.activeFieldId === id ? null : state.activeFieldId,
    }));
  },

  getActiveField: () => {
    const { fields, activeFieldId } = get();
    return fields.find((field) => field.id === activeFieldId) || null;
  },
}));
