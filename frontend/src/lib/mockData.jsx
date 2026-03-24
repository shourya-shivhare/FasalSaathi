import { ACTION_CARD_TYPES } from './constants.jsx';

export const mockFields = [
  {
    id: 'field-1',
    name: 'North Field',
    crop: 'Wheat',
    area: 4.5,
    areaUnit: 'acres',
    location: { lat: 28.6139, lng: 77.2090, village: 'Narela', district: 'Delhi' },
    soilType: 'Loamy',
    sensors: { moisture: 65, temperature: 28, ph: 6.8 },
    growthStage: 'Tillering Stage',
    soilHealth: { score: 78, N: 245, P: 28, K: 195, pH: 6.8 },
  },
  {
    id: 'field-2',
    name: 'South Field',
    crop: 'Soybean',
    area: 2.0,
    areaUnit: 'acres',
    location: { lat: 28.6139, lng: 77.2090, village: 'Narela', district: 'Delhi' },
    soilType: 'Sandy',
    sensors: { moisture: 58, temperature: 29, ph: 6.5 },
    growthStage: 'Flowering Stage',
    soilHealth: { score: 72, N: 265, P: 25, K: 185, pH: 6.5 },
  },
];

export const mockWeather = {
  temp: 34,
  humidity: 68,
  windSpeed: 12,
  condition: 'Partly Cloudy',
  riskLevel: 'HIGH',
  lastUpdated: new Date(Date.now() - 15 * 60 * 1000),
  forecast: [
    { day: 'Mon', high: 36, low: 28, condition: 'Sunny' },
    { day: 'Tue', high: 35, low: 27, condition: 'Partly Cloudy' },
    { day: 'Wed', high: 33, low: 26, condition: 'Rainy' },
    { day: 'Thu', high: 34, low: 27, condition: 'Cloudy' },
    { day: 'Fri', high: 35, low: 28, condition: 'Sunny' },
  ],
};

export const mockSoil = {
  N: 245,
  P: 28,
  K: 195,
  pH: 6.8,
  moisture: 65,
};

export const mockIrrigation = {
  nextScheduled: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
  lastRun: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
  durationMins: 45,
  weeklyUsage: [120, 95, 110, 85, 100, 90, 105],
};

export const mockAlerts = [
  {
    id: 'alert-1',
    type: 'nutrient_deficiency',
    title: 'Low Nitrogen',
    message: 'North Field shows nitrogen deficiency',
    severity: 'high',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    icon: 'AlertTriangle',
  },
  {
    id: 'alert-2',
    type: 'weather_warning',
    title: 'Heat Wave Expected',
    message: 'Temperature may exceed 40°C tomorrow',
    severity: 'medium',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
    icon: 'Thermometer',
  },
  {
    id: 'alert-3',
    type: 'pest_detection',
    title: 'Aphid Activity',
    message: 'Pest activity detected in South Field',
    severity: 'low',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    icon: 'Bug',
  },
];

export const mockMandiPrices = [
  { date: '2024-03-18', price: 2850, volume: 1200 },
  { date: '2024-03-19', price: 2920, volume: 980 },
  { date: '2024-03-20', price: 2880, volume: 1100 },
  { date: '2024-03-21', price: 2950, volume: 850 },
  { date: '2024-03-22', price: 3010, volume: 920 },
  { date: '2024-03-23', price: 2980, volume: 1050 },
  { date: '2024-03-24', price: 3040, volume: 890 },
];

export const mockMSPPrices = [
  { crop: 'Wheat', msp2024: 2275, msp2023: 2125, change: 7.1 },
  { crop: 'Rice', msp2024: 2380, msp2023: 2200, change: 8.2 },
  { crop: 'Cotton', msp2024: 7080, msp2023: 6620, change: 6.9 },
  { crop: 'Soybean', msp2024: 4300, msp2023: 3990, change: 7.8 },
  { crop: 'Maize', msp2024: 2090, msp2023: 1960, change: 6.6 },
  { crop: 'Gram', msp2024: 5335, msp2023: 5080, change: 5.0 },
  { crop: 'Lentil', msp2024: 6425, msp2023: 6000, change: 7.1 },
  { crop: 'Mustard', msp2024: 5450, msp2023: 5100, change: 6.9 },
  { crop: 'Sugarcane', msp2024: 305, msp2023: 290, change: 5.2 },
  { crop: 'Jute', msp2024: 5050, msp2023: 4750, change: 6.3 },
];

export const mockSchemes = [
  {
    id: 'scheme-1',
    name: 'PM-Kisan Samman Nidhi',
    ministry: 'Ministry of Agriculture',
    benefit: '₹6,000 per year',
    deadline: new Date(Date.now() + 25 * 24 * 60 * 60 * 1000),
    eligibility: ['Small marginal farmers', 'Land holding < 2 hectares', 'Valid Aadhar'],
    description: 'Direct income support scheme for farmers',
  },
  {
    id: 'scheme-2',
    name: 'Soil Health Card Scheme',
    ministry: 'Ministry of Agriculture',
    benefit: 'Free soil testing',
    deadline: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
    eligibility: ['All farmers', 'With agricultural land'],
    description: 'Periodic assessment of soil health',
  },
  {
    id: 'scheme-3',
    name: 'Pradhan Mantri Krishi Sinchai Yojana',
    ministry: 'Ministry of Water Resources',
    benefit: 'Up to 55% subsidy',
    deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
    eligibility: ['Micro irrigation', 'Water conservation projects'],
    description: 'Promote efficient water irrigation',
  },
  {
    id: 'scheme-4',
    name: 'e-NAM National Agriculture Market',
    ministry: 'Ministry of Agriculture',
    benefit: 'Better price discovery',
    deadline: null,
    eligibility: ['All farmers', 'Mandi traders'],
    description: 'Online trading platform for agricultural commodities',
  },
];

export const mockPestAlerts = [
  {
    id: 'pest-1',
    pestName: 'Aphids',
    affectedCrop: 'Wheat',
    affectedStates: ['Punjab', 'Haryana', 'Delhi', 'UP'],
    severity: 'Medium',
    preventionTip: 'Monitor crop regularly and use neem oil spray',
  },
  {
    id: 'pest-2',
    pestName: 'Bollworm',
    affectedCrop: 'Cotton',
    affectedStates: ['Gujarat', 'Maharashtra', 'Telangana'],
    severity: 'High',
    preventionTip: 'Use pheromone traps and biological control methods',
  },
  {
    id: 'pest-3',
    pestName: 'Leaf Folder',
    affectedCrop: 'Rice',
    affectedStates: ['West Bengal', 'Odisha', 'Andhra Pradesh'],
    severity: 'Low',
    preventionTip: 'Maintain proper water management and use resistant varieties',
  },
];

export const mockChatMessages = [
  {
    id: 'msg-1',
    role: 'user',
    text: 'My wheat crop leaves are turning yellow. What should I do?',
    timestamp: new Date(Date.now() - 10 * 60 * 1000),
  },
  {
    id: 'msg-2',
    role: 'agent',
    text: 'I understand your concern about yellowing wheat leaves. Let me analyze the possible causes and provide specific recommendations.',
    timestamp: new Date(Date.now() - 8 * 60 * 1000),
  },
  {
    id: 'msg-3',
    role: 'agent',
    text: 'Based on your field data, the yellowing is likely due to nitrogen deficiency. Your soil shows N levels at 245 kg/ha, which is below the optimal range of 280-320 kg/ha.',
    timestamp: new Date(Date.now() - 6 * 60 * 1000),
    actionCard: {
      type: ACTION_CARD_TYPES.FERTILIZER,
      data: {
        nutrients: [
          { name: 'Nitrogen (N)', current: 245, recommended: 300, unit: 'kg/ha' },
          { name: 'Phosphorus (P)', current: 28, recommended: 25, unit: 'kg/ha' },
          { name: 'Potassium (K)', current: 195, recommended: 200, unit: 'kg/ha' },
        ],
        recommendation: 'Apply urea @ 50 kg/ha through top dressing. Split application recommended for better efficiency.',
        fertilizer: 'Urea 46% N',
        applicationRate: '50 kg/ha',
        timing: 'Early morning or late evening',
      },
    },
  },
];

export const mockAgentSteps = [
  { id: 'step-1', label: 'Analyzing field data', status: 'done', detail: 'Soil N levels checked' },
  { id: 'step-2', label: 'Checking symptoms database', status: 'done', detail: 'Matched with nutrient deficiency' },
  { id: 'step-3', label: 'Calculating fertilizer requirements', status: 'done', detail: 'Based on crop stage and soil test' },
  { id: 'step-4', label: 'Preparing recommendations', status: 'pending', detail: 'Generating action plan' },
];
