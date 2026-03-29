import React from 'react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { ProgressBar } from '../../../components/ui/ProgressBar';
import { NUTRIENT_THRESHOLDS } from '../../../lib/constants.jsx';

const SoilHealthGrid = ({ soil }) => {
  const getNutrientStatus = (nutrient, value) => {
    const threshold = NUTRIENT_THRESHOLDS[nutrient];
    if (!threshold) return 'good';

    const isGood = value >= threshold.min && value <= threshold.max;
    return isGood ? 'good' : 'attention';
  };

  const getProgressBarColor = (status) => {
    return status === 'good' ? 'green' : 'red';
  };

  const getProgressBarValue = (nutrient, value) => {
    const threshold = NUTRIENT_THRESHOLDS[nutrient];
    if (!threshold) return 50;

    const range = threshold.max - threshold.min;
    const normalized = (value - threshold.min) / range;
    return Math.max(0, Math.min(100, normalized * 100));
  };

  const nutrients = [
    { key: 'N', name: 'Nitrogen', value: soil.N, unit: 'kg/ha' },
    { key: 'P', name: 'Phosphorus', value: soil.P, unit: 'kg/ha' },
    { key: 'K', name: 'Potassium', value: soil.K, unit: 'kg/ha' },
    { key: 'pH', name: 'pH Level', value: soil.pH, unit: '' },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {nutrients.map((nutrient) => {
        const status = getNutrientStatus(nutrient.key, nutrient.value);
        const progressValue = getProgressBarValue(nutrient.key, nutrient.value);

        return (
          <Card key={nutrient.key} className="p-3 transition-all duration-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium theme-text-primary transition-colors duration-200">
                {nutrient.name}
              </span>
              <Badge variant={status === 'good' ? 'success' : 'danger'}>
                {status === 'good' ? 'Good' : 'Needs Attention'}
              </Badge>
            </div>
            
            <div className="text-lg font-semibold theme-text-primary mb-2 transition-colors duration-200">
              {nutrient.value}
              {nutrient.unit && <span className="text-sm font-normal theme-text-secondary ml-1 transition-colors duration-200"> {nutrient.unit}</span>}
            </div>
            
            <ProgressBar
              value={progressValue}
              colorScheme={getProgressBarColor(status)}
              className="mb-1"
            />
          </Card>
        );
      })}
    </div>
  );
};

export { SoilHealthGrid };
