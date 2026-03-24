// Mock API functions for demonstration
// In a real app, these would make actual HTTP requests

export const api = {
  // Weather API
  async getWeather(coords) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      temp: Math.round(20 + Math.random() * 15),
      humidity: Math.round(40 + Math.random() * 40),
      windSpeed: Math.round(5 + Math.random() * 20),
      condition: ['Sunny', 'Partly Cloudy', 'Cloudy', 'Rainy'][Math.floor(Math.random() * 4)],
      riskLevel: ['LOW', 'MODERATE', 'HIGH'][Math.floor(Math.random() * 3)],
      lastUpdated: new Date(),
    };
  },

  // Market prices API
  async getMarketPrices(crop) {
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const basePrice = 2500 + Math.random() * 1000;
    return {
      currentPrice: Math.round(basePrice),
      mspPrice: Math.round(basePrice * 0.8),
      trend: Math.random() > 0.5 ? 'up' : 'down',
      change: (Math.random() * 10 - 5).toFixed(1),
      mandiName: 'Local Mandi',
      distance: Math.round(5 + Math.random() * 20),
    };
  },

  // Chat API
  async sendMessage(message) {
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      id: `msg-${Date.now()}`,
      role: 'agent',
      text: 'I understand your question. Based on your field data and current conditions, here are my recommendations...',
      timestamp: new Date(),
      actionCard: {
        type: 'fertilizer',
        data: {
          nutrients: [
            { name: 'Nitrogen (N)', current: 245, recommended: 300, unit: 'kg/ha' },
            { name: 'Phosphorus (P)', current: 28, recommended: 25, unit: 'kg/ha' },
            { name: 'Potassium (K)', current: 195, recommended: 200, unit: 'kg/ha' },
          ],
          recommendation: 'Apply urea @ 50 kg/ha through top dressing.',
          fertilizer: 'Urea 46% N',
          applicationRate: '50 kg/ha',
          timing: 'Early morning or late evening',
        },
      },
    };
  },

  // Schemes API
  async getSchemes() {
    await new Promise(resolve => setTimeout(resolve, 600));
    
    return [
      {
        id: 'scheme-1',
        name: 'PM-Kisan Samman Nidhi',
        ministry: 'Ministry of Agriculture',
        benefit: '₹6,000 per year',
        deadline: new Date(Date.now() + 25 * 24 * 60 * 60 * 1000),
        eligibility: ['Small marginal farmers', 'Land holding < 2 hectares'],
      },
    ];
  },

  // Pest alerts API
  async getPestAlerts(crop, state) {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return [
      {
        id: 'pest-1',
        pestName: 'Aphids',
        affectedCrop: crop,
        severity: 'Medium',
        preventionTip: 'Monitor crop regularly and use neem oil spray',
      },
    ];
  },

  // Field data API
  async saveFieldData(fieldData) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      ...fieldData,
      id: `field-${Date.now()}`,
      createdAt: new Date(),
    };
  },

  // User profile API
  async updateUserProfile(profileData) {
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return {
      ...profileData,
      updatedAt: new Date(),
    };
  },
};

export default api;
