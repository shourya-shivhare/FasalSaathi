import { useEffect } from 'react';
import { useFieldStore } from '../../../stores/useFieldStore.jsx';

export const useFieldData = () => {
  const {
    fields,
    activeFieldId,
    weather,
    soil,
    irrigation,
    setActiveField,
    fetchWeather,
    updateSensorData,
    getActiveField,
  } = useFieldStore();

  const activeField = getActiveField();

  useEffect(() => {
    // Fetch weather data for active field location
    if (activeField?.location) {
      fetchWeather(activeField.location);
    }
  }, [activeField, fetchWeather]);

  useEffect(() => {
    // Simulate real-time sensor data updates
    const interval = setInterval(() => {
      if (activeField) {
        updateSensorData({
          moisture: 60 + Math.random() * 20,
          temperature: 25 + Math.random() * 10,
          ph: 6.5 + Math.random() * 0.5,
        });
      }
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [activeField, updateSensorData]);

  return {
    fields,
    activeField,
    weather,
    soil,
    irrigation,
    setActiveField,
    hasFields: fields.length > 0,
    isLoading: !weather || !soil,
  };
};
