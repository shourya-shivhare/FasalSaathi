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

  fetchWeather: async (coords) => {
    // Simulate API call
    set({ isWeatherLoading: true });
    
    setTimeout(() => {
      const updatedWeather = {
        ...mockWeather,
        temp: Math.round(25 + Math.random() * 15),
        humidity: Math.round(50 + Math.random() * 30),
        windSpeed: Math.round(5 + Math.random() * 20),
        lastUpdated: new Date(),
      };

      set({ weather: updatedWeather, isWeatherLoading: false });
    }, 1000);
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
