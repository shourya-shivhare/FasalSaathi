import React, { useState } from 'react';
import {
  Sprout, Search, Filter, Loader2, AlertTriangle,
  Droplets, Sun, ChevronDown, ChevronUp, Wheat, Leaf,
} from 'lucide-react';
import { api } from '../../lib/api.jsx';
import { useUserStore } from '../../stores/useUserStore.jsx';

// ── Constants ────────────────────────────────────────────────────────────────

const STATES = [
  'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh',
  'Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka',
  'Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram',
  'Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu',
  'Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal','Delhi',
];

const SOIL_TYPES = ['Loamy', 'Alluvial', 'Clayey', 'Sandy', 'Black', 'Red', 'Laterite'];
const SEASONS = ['Kharif', 'Rabi', 'Zaid'];
const WATER_LEVELS = ['low', 'moderate', 'high', 'irrigated'];

// ── Crop emoji map ───────────────────────────────────────────────────────────
const cropEmoji = (name) => {
  const n = name.toLowerCase();
  if (n.includes('rice') || n.includes('paddy')) return '🌾';
  if (n.includes('wheat')) return '🌾';
  if (n.includes('maize') || n.includes('corn')) return '🌽';
  if (n.includes('cotton')) return '🧵';
  if (n.includes('soybean') || n.includes('soya')) return '🫘';
  if (n.includes('mustard')) return '🌻';
  if (n.includes('gram') || n.includes('chana') || n.includes('pulse')) return '🫛';
  if (n.includes('moong') || n.includes('mung')) return '🫛';
  if (n.includes('watermelon')) return '🍉';
  if (n.includes('cucumber')) return '🥒';
  if (n.includes('tomato')) return '🍅';
  if (n.includes('potato')) return '🥔';
  if (n.includes('onion')) return '🧅';
  if (n.includes('sugarcane')) return '🎋';
  return '🌱';
};

// ── Component ────────────────────────────────────────────────────────────────

export const CropSuggestionPage = () => {
  const farmer = useUserStore((s) => s.farmer);
  const accessToken = useUserStore((s) => s.accessToken);

  // Form state — pre-filled from profile
  const [state, setState] = useState(farmer?.state || '');
  const [district, setDistrict] = useState(farmer?.district || '');
  const [soilType, setSoilType] = useState('Loamy');
  const [season, setSeason] = useState('Kharif');
  const [waterAvailability, setWaterAvailability] = useState('moderate');
  const [landSize, setLandSize] = useState(farmer?.land_size_acres || '');
  const [pastCrops, setPastCrops] = useState(
    Array.isArray(farmer?.crops_grown) ? farmer.crops_grown.join(', ') : (farmer?.crops_grown || '')
  );

  // Results
  const [crops, setCrops] = useState([]);
  const [summary, setSummary] = useState('');
  const [pestNote, setPestNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedIdx, setExpandedIdx] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!state) { setError('Please select a state'); return; }
    setLoading(true);
    setError(null);
    setCrops([]);
    setHasSearched(true);
    try {
      const payload = {
        state,
        district: district || undefined,
        soil_type: soilType,
        season,
        water_availability: waterAvailability,
        land_size_acres: landSize ? parseFloat(landSize) : undefined,
        past_crops: pastCrops ? pastCrops.split(',').map(c => c.trim()).filter(Boolean) : [],
      };
      const data = await api.getCropRecommendation(payload, accessToken);
      setCrops(data.recommended_crops || []);
      setSummary(data.reasoning_summary || '');
      setPestNote(data.pest_considerations || '');
    } catch (err) {
      setError(err.message || 'Failed to fetch crop recommendations');
    } finally {
      setLoading(false);
    }
  };

  // ── Score helpers ────────────────────────────────────────────────────────
  const scoreColor = (score) => {
    if (score >= 0.8) return '#22c55e';
    if (score >= 0.5) return '#f59e0b';
    return '#ef4444';
  };

  const scoreLabel = (score) => {
    if (score >= 0.8) return 'Highly Recommended';
    if (score >= 0.5) return 'Good Match';
    return 'Worth Considering';
  };

  // ── Styles ──────────────────────────────────────────────────────────────
  const pageStyle = {
    padding: '32px', maxWidth: '1100px', margin: '0 auto',
    fontFamily: "'Inter', sans-serif", color: '#E8F5E9',
  };
  const headerStyle = {
    display: 'flex', alignItems: 'center', gap: '14px',
    marginBottom: '8px',
  };
  const h1Style = {
    fontSize: '1.8rem', fontWeight: 800, margin: 0,
    fontFamily: "'Plus Jakarta Sans', sans-serif",
    background: 'linear-gradient(135deg, #4ADE80, #22c55e)',
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
  };
  const subtitleStyle = {
    color: 'rgba(255,255,255,0.55)', fontSize: '0.95rem', marginBottom: '28px',
  };
  const formGrid = {
    display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
    gap: '16px', marginBottom: '24px',
  };
  const inputStyle = {
    width: '100%', padding: '12px 14px', borderRadius: '12px',
    background: 'rgba(0,0,0,0.25)', border: '1px solid rgba(255,255,255,0.1)',
    color: '#fff', fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box',
  };
  const labelStyle = {
    display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: '0.8rem',
    fontWeight: 600, marginBottom: '6px',
  };
  const btnStyle = {
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
    padding: '14px 32px', borderRadius: '14px', border: 'none',
    background: 'linear-gradient(135deg, #1A7A40, #2D9450)', color: '#fff',
    fontSize: '1rem', fontWeight: 700, cursor: 'pointer',
    boxShadow: '0 4px 20px rgba(26,122,64,0.4)', transition: 'all 0.2s',
  };
  const cardStyle = {
    background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(16px)',
    border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px',
    padding: '20px 24px', marginBottom: '14px', transition: 'all 0.2s',
  };
  const pillStyle = {
    display: 'inline-flex', alignItems: 'center', gap: '4px',
    padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem',
    fontWeight: 600,
  };

  return (
    <div style={pageStyle}>
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div style={headerStyle}>
        <div style={{
          width: '44px', height: '44px', borderRadius: '12px',
          background: 'linear-gradient(135deg, #1A7A40, #2D8F55)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 16px rgba(26,122,64,0.4)',
        }}>
          <Sprout size={22} color="#fff" />
        </div>
        <h1 style={h1Style}>Crop Suggestions</h1>
      </div>
      <p style={subtitleStyle}>
        AI-powered crop recommendations based on your soil, season, and local conditions
      </p>

      {/* ── Filter Form ─────────────────────────────────────────────────── */}
      <div style={{
        background: 'rgba(255,255,255,0.04)', backdropFilter: 'blur(12px)',
        border: '1px solid rgba(255,255,255,0.08)', borderRadius: '20px',
        padding: '24px', marginBottom: '28px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '18px' }}>
          <Filter size={16} color="#4ADE80" />
          <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Your Farm Details</span>
          <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.8rem', marginLeft: '8px' }}>
            (auto-filled from your profile — edit to refine)
          </span>
        </div>

        <div style={formGrid}>
          <div>
            <label style={labelStyle}>State *</label>
            <select value={state} onChange={e => setState(e.target.value)} style={inputStyle}>
              <option value="">Select State</option>
              {STATES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>District</label>
            <input value={district} onChange={e => setDistrict(e.target.value)}
              placeholder="e.g. Lucknow" style={inputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Soil Type</label>
            <select value={soilType} onChange={e => setSoilType(e.target.value)} style={inputStyle}>
              {SOIL_TYPES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Season</label>
            <select value={season} onChange={e => setSeason(e.target.value)} style={inputStyle}>
              {SEASONS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Water Availability</label>
            <select value={waterAvailability} onChange={e => setWaterAvailability(e.target.value)} style={inputStyle}>
              {WATER_LEVELS.map(w => <option key={w} value={w}>{w.charAt(0).toUpperCase() + w.slice(1)}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Land Size (acres)</label>
            <input type="number" value={landSize} onChange={e => setLandSize(e.target.value)}
              placeholder="e.g. 2.5" style={inputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Past Crops (comma-separated)</label>
            <input value={pastCrops} onChange={e => setPastCrops(e.target.value)}
              placeholder="e.g. Wheat, Rice" style={inputStyle} />
          </div>
        </div>

        <button onClick={handleSearch} disabled={loading} style={{
          ...btnStyle, opacity: loading ? 0.7 : 1,
          cursor: loading ? 'not-allowed' : 'pointer',
        }}>
          {loading
            ? <><Loader2 size={18} className="spin" /> Analyzing soil & conditions...</>
            : <><Search size={18} /> Get Crop Recommendations</>
          }
        </button>
      </div>

      {/* ── Error ───────────────────────────────────────────────────────── */}
      {error && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '14px 18px', borderRadius: '12px',
          background: 'rgba(220,38,38,0.15)', border: '1px solid rgba(248,113,113,0.3)',
          color: '#fecaca', marginBottom: '20px', fontSize: '0.9rem',
        }}>
          <AlertTriangle size={18} /> {error}
        </div>
      )}

      {/* ── Summary bar ─────────────────────────────────────────────────── */}
      {hasSearched && !loading && crops.length > 0 && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '12px 18px', borderRadius: '12px',
          background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.15)',
          marginBottom: '20px', fontSize: '0.85rem', color: 'rgba(255,255,255,0.7)',
        }}>
          <Sprout size={16} color="#4ADE80" />
          <span>
            <strong style={{ color: '#4ADE80' }}>{crops.length}</strong> crops recommended. {summary}
          </span>
        </div>
      )}

      {/* Pest considerations */}
      {pestNote && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '12px 18px', borderRadius: '12px',
          background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.15)',
          marginBottom: '20px', fontSize: '0.85rem', color: 'rgba(255,255,255,0.7)',
        }}>
          <AlertTriangle size={16} color="#f59e0b" />
          <span>🐛 {pestNote}</span>
        </div>
      )}

      {/* No results */}
      {hasSearched && !loading && crops.length === 0 && !error && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '12px 18px', borderRadius: '12px',
          background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.15)',
          marginBottom: '20px', fontSize: '0.85rem', color: 'rgba(255,255,255,0.7)',
        }}>
          <Sprout size={16} color="#4ADE80" />
          <span>No recommendations available. Try adjusting your parameters.</span>
        </div>
      )}

      {/* ── Crop Result Cards ───────────────────────────────────────────── */}
      {crops.map((crop, i) => (
        <div key={i} style={cardStyle}
          onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(74,222,128,0.3)'}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'}>

          {/* Top row: name + confidence */}
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <span style={{ fontSize: '1.4rem' }}>{cropEmoji(crop.crop_name)}</span>
                <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, color: '#fff' }}>
                  {crop.crop_name}
                </h3>
                <span style={{
                  ...pillStyle,
                  background: 'rgba(74,222,128,0.1)', color: '#4ADE80',
                }}>
                  {crop.season}
                </span>
              </div>
            </div>

            {/* Confidence badge */}
            <div style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px',
              padding: '8px 14px', borderRadius: '12px',
              background: `${scoreColor(crop.confidence)}15`,
              border: `1px solid ${scoreColor(crop.confidence)}30`,
              minWidth: '100px',
            }}>
              <span style={{ fontSize: '1.2rem', fontWeight: 800, color: scoreColor(crop.confidence) }}>
                {Math.round(crop.confidence * 100)}%
              </span>
              <span style={{ fontSize: '0.7rem', color: scoreColor(crop.confidence), fontWeight: 600 }}>
                {scoreLabel(crop.confidence)}
              </span>
            </div>
          </div>

          {/* Reasoning */}
          <p style={{
            margin: '12px 0 0', padding: '10px 14px', borderRadius: '10px',
            background: 'rgba(74,222,128,0.06)', fontSize: '0.88rem',
            color: 'rgba(255,255,255,0.8)', lineHeight: 1.5,
          }}>
            {crop.reasoning}
          </p>

          {/* Metadata pills */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
            {crop.estimated_yield_per_acre && (
              <span style={{
                ...pillStyle,
                background: 'rgba(96,165,250,0.1)', color: '#60a5fa',
              }}>
                <Wheat size={12} /> Yield: {crop.estimated_yield_per_acre}
              </span>
            )}
            {crop.water_requirement && (
              <span style={{
                ...pillStyle,
                background: 'rgba(56,189,248,0.1)', color: '#38bdf8',
              }}>
                <Droplets size={12} /> Water: {crop.water_requirement}
              </span>
            )}
          </div>
        </div>
      ))}

      {/* ── Spin animation (shared with SchemesPage) ──────────────────── */}
      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }
      `}</style>
    </div>
  );
};
