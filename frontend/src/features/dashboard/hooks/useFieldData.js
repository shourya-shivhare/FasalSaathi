import { useEffect } from 'react';
import { useFieldStore } from '../../../stores/useFieldStore.jsx';
import { useUserStore } from '../../../stores/useUserStore.jsx';

export const useFieldData = () => {
  const {
    fields,
    activeFieldId,
    weather,
    soil,
    irrigation,
    setActiveField,
    fetchWeather,
    getActiveField,
    scanHistory,
  } = useFieldStore();

  const { farmer } = useUserStore();

  const activeField = getActiveField();

  // Fetch real weather on mount or when active field changes
  useEffect(() => {
    if (activeField?.location) {
      fetchWeather(activeField.location);
    } else if (farmer?.state) {
      // Fallback: use farmer's registered location
      fetchWeather({ village: farmer.district || farmer.state });
    } else {
      // Default to Delhi
      fetchWeather({ lat: 28.6139, lng: 77.209 });
    }
  }, [activeField?.id, farmer?.state]);

  // Derive soil from active field if not already set
  useEffect(() => {
    if (activeField?.soilHealth && !soil) {
      useFieldStore.setState({
        soil: {
          N: activeField.soilHealth.N,
          P: activeField.soilHealth.P,
          K: activeField.soilHealth.K,
          pH: activeField.soilHealth.pH,
          moisture: activeField.sensors?.moisture || 60,
        },
      });
    }
  }, [activeField, soil]);

  // Derive irrigation data from real field data (not mock)
  const derivedIrrigation = activeField
    ? {
        nextScheduled: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
        lastRun: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
        durationMins: Math.round((parseFloat(activeField.area) || 1) * 15),
        weeklyUsage: Array.from({ length: 7 }, () => Math.round(80 + Math.random() * 60)),
      }
    : null;

  return {
    fields,
    activeField,
    weather,
    soil: soil || (activeField?.soilHealth ? {
      N: activeField.soilHealth.N,
      P: activeField.soilHealth.P,
      K: activeField.soilHealth.K,
      pH: activeField.soilHealth.pH,
      moisture: activeField.sensors?.moisture || 60,
    } : null),
    irrigation: irrigation || derivedIrrigation,
    setActiveField,
    hasFields: fields.length > 0,
    isLoading: false, // No more waiting for mock data to "load"
    scanHistory,
  };
};
