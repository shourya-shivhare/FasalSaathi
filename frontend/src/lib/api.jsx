// src/lib/api.jsx
// Real API client — replaces the old mock layer.
// Chat is handled by useChatStore directly.

const AI_BASE = 'http://localhost:8001'; // ai-service direct (for detect fallback)
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// ── helpers ────────────────────────────────────────────────────────────────

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Weather — Open-Meteo (free, no API key) ────────────────────────────────

export const api = {
  async getWeather(coords) {
    const { lat = 28.6139, lon = 77.2090 } = coords || {};
    // Try backend proxy first (it also calls Open-Meteo)
    try {
      const data = await fetchJSON(`${API_BASE}/weather/current?lat=${lat}&lon=${lon}`);
      return data; // already in the right shape
    } catch { /* backend down — fall through to direct call */ }

    // Direct Open-Meteo fallback (no key needed)
    try {
      const data = await fetchJSON(
        `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}` +
        `&current_weather=true&hourly=relativehumidity_2m,windspeed_10m&forecast_days=1`
      );
      const cw = data.current_weather;
      const humidity = data.hourly?.relativehumidity_2m?.[0] ?? 60;
      const windSpeed = data.hourly?.windspeed_10m?.[0] ?? 12;
      const conditionMap = {
        0: 'Sunny', 1: 'Partly Cloudy', 2: 'Partly Cloudy', 3: 'Cloudy',
        45: 'Foggy', 61: 'Rainy', 80: 'Showers', 95: 'Thunderstorm',
      };
      const condition = conditionMap[cw?.weathercode ?? 0] ?? 'Clear';
      const temp = Math.round(cw?.temperature ?? 28);
      const riskLevel = humidity > 80 ? 'HIGH' : humidity > 60 ? 'MODERATE' : 'LOW';
      return { temp, humidity, windSpeed: Math.round(windSpeed), condition, riskLevel, lastUpdated: new Date() };
    } catch { /* offline */ }

    return { temp: 28, humidity: 58, windSpeed: 12, condition: 'Sunny', riskLevel: 'LOW', lastUpdated: new Date() };
  },


  // ── Market prices — enriched static data (no public mandi API) ─────────
  async getMarketPrices(crop = 'Wheat') {
    const prices = {
      Wheat:  { base: 2275, msp: 2150 },
      Rice:   { base: 2183, msp: 2183 },
      Maize:  { base: 1962, msp: 1875 },
      Cotton: { base: 6380, msp: 6025 },
      Soybean:{ base: 4600, msp: 4300 },
    };
    const p = prices[crop] || prices.Wheat;
    const jitter = Math.round((Math.random() - 0.5) * 80);
    const current = p.base + jitter;
    const change = ((jitter / p.base) * 100).toFixed(1);
    return {
      currentPrice: current,
      mspPrice: p.msp,
      trend: jitter >= 0 ? 'up' : 'down',
      change,
      mandiName: 'Narela Mandi',
      distance: 8,
    };
  },

  // ── Schemes — enriched static data ─────────────────────────────────────
  async getSchemes() {
    return [
      {
        id: 'scheme-1',
        name: 'PM-Kisan Samman Nidhi',
        ministry: 'Ministry of Agriculture',
        benefit: '₹6,000 per year',
        deadline: new Date(Date.now() + 25 * 24 * 60 * 60 * 1000),
        eligibility: ['Small marginal farmers', 'Land holding < 2 hectares'],
      },
      {
        id: 'scheme-2',
        name: 'Pradhan Mantri Fasal Bima Yojana',
        ministry: 'Ministry of Agriculture',
        benefit: 'Crop insurance at 2% premium',
        deadline: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
        eligibility: ['All farmers growing notified crops'],
      },
      {
        id: 'scheme-3',
        name: 'Kisan Credit Card',
        ministry: 'NABARD / Banks',
        benefit: 'Credit up to ₹3 lakh @ 4% interest',
        deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
        eligibility: ['Individual farmers', 'Tenant farmers', 'SHGs'],
      },
    ];
  },

  // ── Pest alerts — enriched static data ─────────────────────────────────
  async getPestAlerts(crop = 'Wheat', state = 'Delhi') {
    const alerts = {
      Wheat: [
        { id: 'p1', pestName: 'Aphids (Maahu)', affectedCrop: 'Wheat', severity: 'Medium', preventionTip: 'Spray Imidacloprid 0.5ml/L water in early morning' },
        { id: 'p2', pestName: 'Yellow Rust', affectedCrop: 'Wheat', severity: 'High', preventionTip: 'Apply Propiconazole 25 EC @ 0.1% at first sign' },
      ],
      Rice: [
        { id: 'p3', pestName: 'Brown Plant Hopper', affectedCrop: 'Rice', severity: 'High', preventionTip: 'Avoid excess nitrogen; use Buprofezin 25 SC' },
      ],
    };
    return alerts[crop] || alerts.Wheat;
  },

  // ── Field data — local persist ──────────────────────────────────────────
  async saveFieldData(fieldData) {
    // Persist to backend if available, else localStorage
    try {
      return await fetchJSON(`${API_BASE}/crops`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fieldData),
      });
    } catch {
      const saved = { ...fieldData, id: `field-${Date.now()}`, createdAt: new Date() };
      localStorage.setItem('fasalsaathi_field', JSON.stringify(saved));
      return saved;
    }
  },

  // ── User profile ────────────────────────────────────────────────────────
  async updateUserProfile(profileData) {
    localStorage.setItem('fasalsaathi_profile', JSON.stringify({ ...profileData, updatedAt: new Date() }));
    return { ...profileData, updatedAt: new Date() };
  },

  // ── Pest Detection — calls backend proxy which calls ai-service YOLO ───
  async detectPest(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    // Try backend first (has YOLO weight path setup), fallback to ai-service direct
    try {
      return await fetchJSON(`${API_BASE}/detect`, { method: 'POST', body: formData });
    } catch {
      return await fetchJSON(`${AI_BASE}/detect`, { method: 'POST', body: formData });
    }
  },
};

export default api;
