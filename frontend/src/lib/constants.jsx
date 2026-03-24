export const NUTRIENT_THRESHOLDS = {
  N: { min: 280, max: 320, unit: 'kg/ha' },
  P: { min: 20, max: 30, unit: 'kg/ha' },
  K: { min: 180, max: 220, unit: 'kg/ha' },
  pH: { min: 6.0, max: 7.5, unit: '' },
};

export const CROP_TYPES = [
  'Wheat',
  'Rice',
  'Cotton',
  'Soybean',
  'Maize',
  'Other',
];

export const SOIL_TYPES = [
  'Sandy',
  'Loamy',
  'Clay',
  'Black Cotton',
];

export const GROWTH_STAGES = [
  'Sowing',
  'Germination',
  'Vegetative',
  'Flowering',
  'Harvest',
];

export const ALERT_TYPES = {
  NUTRIENT_DEFICIENCY: 'nutrient_deficiency',
  WEATHER_WARNING: 'weather_warning',
  PEST_DETECTION: 'pest_detection',
  SCHEME_DEADLINE: 'scheme_deadline',
};

export const ACTION_CARD_TYPES = {
  FERTILIZER: 'fertilizer',
  IRRIGATION: 'irrigation',
  PEST_ALERT: 'pest_alert',
  SCHEME: 'scheme',
  MARKET_PRICE: 'market_price',
};
