import { useEffect, useState } from 'react';
import { useFieldStore } from '../../../stores/useFieldStore.jsx';
import { useUserStore } from '../../../stores/useUserStore.jsx';
import { useFarmStore } from '../../../stores/useFarmStore.jsx';
import { useCropCycleStore } from '../../../stores/useCropCycleStore.jsx';
import api from '../../../lib/api.jsx';

export const useFieldData = () => {
  const { activeFieldId, weather, setActiveField, fetchWeather } = useFieldStore();
  const { farmer, accessToken } = useUserStore();
  const { farms, fetchFarms } = useFarmStore();
  const { cycles, fetchCycles } = useCropCycleStore();

  const [scanHistory, setScanHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load farms and cycles on mount
  useEffect(() => {
    fetchFarms();
    fetchCycles();
  }, []);

  // Load scan history from backend
  useEffect(() => {
    let active = true;
    if (accessToken) {
      setIsLoading(true);
      api.getPestHistory(accessToken)
        .then(data => {
          if (active) {
            const mapped = data.map(record => ({
              id: record.id,
              pestName: record.disease_name || 'Unknown',
              confidence: record.confidence,
              severity: record.confidence && record.confidence > 0.7 ? 'High' : record.confidence && record.confidence > 0.4 ? 'Medium' : 'Low',
              timestamp: new Date(record.created_at).getTime(),
              message: `${record.disease_name || 'Pest'} was detected with ${record.confidence ? Math.round(record.confidence * 100) : '--'}% confidence.`
            }));
            setScanHistory(mapped);
            setIsLoading(false);
          }
        })
        .catch(err => {
          console.error("Failed to load scan history in hook:", err);
          if (active) setIsLoading(false);
        });
    }
    return () => { active = false; };
  }, [accessToken]);

  // Map farms & cycles to fields
  const fields = farms.map(farm => {
    const activeCycle = cycles.find(c => c.farm_id === farm.id && c.status === 'ACTIVE');
    return {
      id: farm.id,
      name: farm.farm_name,
      area: farm.total_area,
      areaUnit: 'acres',
      crop: activeCycle ? activeCycle.crop_name : null,
      growthStage: activeCycle ? activeCycle.current_stage : 'Vegetative',
      soilType: farm.soil_type,
      location: { village: farm.village, district: farm.district, state: farm.state }
    };
  });

  const activeField = fields.find(f => f.id === activeFieldId) || fields[0] || null;

  // Fetch weather when active field or farmer state changes
  useEffect(() => {
    if (activeField?.location) {
      fetchWeather({
        lat: 28.6139,
        lng: 77.209,
        ...activeField.location
      });
    } else if (farmer?.state) {
      fetchWeather({ state: farmer.state });
    } else {
      fetchWeather({ lat: 28.6139, lng: 77.209 });
    }
  }, [activeField?.id, farmer?.state]);

  return {
    fields,
    activeField,
    weather,
    soil: null, // Strictly null. No fabricated values!
    irrigation: null, // Strictly null. No fabricated values!
    setActiveField,
    hasFields: fields.length > 0,
    isLoading,
    scanHistory
  };
};
