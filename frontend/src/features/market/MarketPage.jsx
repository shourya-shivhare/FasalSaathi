import React, { useState, useEffect, useCallback } from 'react';
import {
  TrendingUp, TrendingDown, RefreshCw, MapPin, BarChart2,
  ArrowUpRight, Target, Loader2, AlertCircle, ShieldCheck, Activity,
} from 'lucide-react';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { PriceTrendChart } from './components/PriceTrendChart';
import { useFieldStore } from '../../stores/useFieldStore.jsx';
import api from '../../lib/api.jsx';

// ── Constants ───────────────────────────────────────────────────────────────
const DEFAULT_COMMODITIES = ['Wheat', 'Rice', 'Soybean', 'Cotton', 'Maize', 'Mustard', 'Gram', 'Sunflower'];

const mspData = [
  { crop: 'Wheat',    msp: 2275, icon: '🌾' },
  { crop: 'Rice',     msp: 2183, icon: '🍚' },
  { crop: 'Soybean',  msp: 4600, icon: '🫘' },
  { crop: 'Cotton',   msp: 6620, icon: '🌿' },
  { crop: 'Maize',    msp: 2090, icon: '🌽' },
  { crop: 'Mustard',  msp: 5650, icon: '🌻' },
  { crop: 'Gram',     msp: 5440, icon: '🫛' },
  { crop: 'Sunflower',msp: 6760, icon: '🌸' },
];

const cropIcons = { Wheat: '🌾', Rice: '🍚', Soybean: '🫘', Cotton: '🌿', Maize: '🌽', Mustard: '🌻', Gram: '🫛', Sunflower: '🌸' };

const generate30Day = () => {
  const data = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date(); d.setDate(d.getDate() - i);
    const price = Math.round(2900 + Math.sin(i * 0.3) * 200 + Math.random() * 100);
    data.push({ date: d.toISOString().split('T')[0], price, volume: Math.round(800 + Math.random() * 600) });
  }
  return data;
};

const riskColors = { LOW: '#10B981', MODERATE: '#F59E0B', HIGH: '#EF4444' };
const riskBg = { LOW: '#D1FAE5', MODERATE: '#FEF3C7', HIGH: '#FEE2E2' };

// ── Component ───────────────────────────────────────────────────────────────
const MarketPage = () => {
  const { getActiveField, fields } = useFieldStore();
  const activeField = getActiveField();

  // Derive user location
  const userState = activeField?.location?.state || activeField?.state || 'Delhi';
  const userDistrict = activeField?.location?.district || activeField?.district || '';

  // Build commodity list: default 8 + crops from user fields, deduplicated
  const fieldCrops = (fields || [])
    .map(f => f.crop || f.cropType)
    .filter(Boolean)
    .filter(c => !DEFAULT_COMMODITIES.includes(c));
  const allCommodities = [...DEFAULT_COMMODITIES, ...new Set(fieldCrops)];

  const [selectedCrop, setSelectedCrop] = useState(activeField?.crop || 'Wheat');
  const [analysisData, setAnalysisData] = useState(null);
  const [rawPrices, setRawPrices] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLiveData, setIsLiveData] = useState(true);

  // ── Fetch market data ──────────────────────────────────────────────────
  const fetchMarketData = useCallback(async (crop) => {
    setLoading(true);
    setError(null);
    try {
      const [analysis, prices] = await Promise.all([
        api.getMarketAnalysis(crop, userState, userDistrict),
        api.getMarketPrices(crop, userState, userDistrict),
      ]);

      if (analysis) {
        setAnalysisData(analysis);
        setIsLiveData(true);
      } else {
        // Build minimal fallback from raw prices
        setAnalysisData(null);
        setIsLiveData(false);
      }
      setRawPrices(prices);
    } catch (err) {
      setError(err.message || 'Failed to fetch market data');
      setIsLiveData(false);
    } finally {
      setLoading(false);
    }
  }, [userState, userDistrict]);

  useEffect(() => {
    fetchMarketData(selectedCrop);
  }, [selectedCrop]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Derived values ─────────────────────────────────────────────────────
  const priceHistory = rawPrices?.records
    ? rawPrices.records.map(r => ({
        date: r.arrival_date || '',
        price: parseInt(r.modal_price) || 0,
        volume: Math.round(800 + Math.random() * 600),
      })).sort((a, b) => a.date.localeCompare(b.date))
    : generate30Day();

  const mspEntry = mspData.find(m => m.crop === selectedCrop);
  const mspPrice = mspEntry?.msp || 2275;
  const icon = cropIcons[selectedCrop] || '🌱';

  const modalPriceNum = analysisData?.current_market_analysis
    ? parseInt(analysisData.current_market_analysis.modal_price.replace(/[^\d]/g, '')) || 0
    : (rawPrices?.records?.[0]?.modal_price || 0);

  const diff = modalPriceNum - mspPrice;

  // ── Loading State ──────────────────────────────────────────────────────
  if (loading) {
    return (
      <PageWrapper>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', gap: '16px' }}>
          <Loader2 size={40} color="var(--color-accent-primary)" style={{ animation: 'spin 1s linear infinite' }} />
          <p style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 600, color: 'var(--color-text-secondary)', fontSize: '1rem' }}>
            Fetching live market data...
          </p>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      </PageWrapper>
    );
  }

  // ── Error State ────────────────────────────────────────────────────────
  if (error && !analysisData && !rawPrices) {
    return (
      <PageWrapper>
        <div style={{ background: '#FEF2F2', borderRadius: '20px', border: '1px solid #FECACA', padding: '32px', textAlign: 'center', marginTop: '40px' }}>
          <AlertCircle size={40} color="#EF4444" style={{ marginBottom: '12px' }} />
          <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.2rem', fontWeight: 700, color: '#991B1B', margin: '0 0 8px' }}>Unable to fetch market data</h2>
          <p style={{ color: '#7F1D1D', fontSize: '0.9rem', marginBottom: '20px' }}>{error}</p>
          <button onClick={() => fetchMarketData(selectedCrop)} style={{
            padding: '10px 24px', borderRadius: '12px', border: 'none', background: '#EF4444', color: '#fff',
            fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '8px'
          }}>
            <RefreshCw size={15} /> Retry
          </button>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      {/* Fallback banner */}
      {!isLiveData && (
        <div style={{ background: '#FEF3C7', border: '1px solid #FDE68A', borderRadius: '12px', padding: '10px 16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: '#92400E' }}>
          <AlertCircle size={16} /> Live data unavailable — showing estimates
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.65rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
            Market Prices
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: '4px 0 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={14} /> {analysisData?.location?.market || userDistrict || userState} · {analysisData?.location?.state || userState}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <select
            id="crop-selector"
            value={selectedCrop}
            onChange={e => setSelectedCrop(e.target.value)}
            style={{
              padding: '10px 16px', borderRadius: '12px', border: '1.5px solid var(--color-border)',
              background: '#fff', fontFamily: "'Plus Jakarta Sans',sans-serif",
              fontWeight: 600, fontSize: '0.875rem', color: 'var(--color-text-primary)',
              cursor: 'pointer', appearance: 'auto',
            }}
          >
            {allCommodities.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <button
            id="refresh-btn"
            onClick={() => fetchMarketData(selectedCrop)}
            style={{
              display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px',
              border: '1.5px solid var(--color-border)', borderRadius: '12px', background: '#fff',
              color: 'var(--color-accent-primary)', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer',
            }}
          >
            <RefreshCw size={15} /> Refresh
          </button>
        </div>
      </div>

      {/* HERO PRICE CARD */}
      <div style={{
        background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)',
        borderLeft: '5px solid #FACC15', padding: '28px 32px', marginBottom: '20px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.07)', display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: 'linear-gradient(135deg,#FEF3C7,#FDE68A)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', flexShrink: 0 }}>{icon}</div>
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>Current Mandi Price</div>
            <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-accent-primary)', lineHeight: 1.1 }}>
              {analysisData?.current_market_analysis?.modal_price || `₹${modalPriceNum.toLocaleString()}`}
            </div>
            <div style={{ fontWeight: 600, color: 'var(--color-text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>{selectedCrop} · per quintal</div>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', alignItems: 'flex-end' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: diff >= 0 ? '#D1FAE5' : '#FEE2E2', borderRadius: '12px', padding: '8px 16px' }}>
            {diff >= 0 ? <ArrowUpRight size={18} color="#065F46" /> : <TrendingDown size={18} color="#DC2626" />}
            <span style={{ fontWeight: 700, color: diff >= 0 ? '#065F46' : '#DC2626', fontSize: '0.95rem' }}>
              ₹{Math.abs(diff)} {diff >= 0 ? 'above' : 'below'} MSP
            </span>
          </div>
          {analysisData?.current_market_analysis?.price_trend && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
              {analysisData.current_market_analysis.price_trend === 'rising' ? <TrendingUp size={14} color="#10B981" /> : analysisData.current_market_analysis.price_trend === 'falling' ? <TrendingDown size={14} color="#EF4444" /> : <Activity size={14} color="#6B7280" />}
              Trend: {analysisData.current_market_analysis.price_trend}
            </div>
          )}
        </div>
      </div>

      {/* MINI STATS ROW */}
      {analysisData && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '20px' }}>
          {[
            {
              label: 'Sentiment',
              value: analysisData.current_market_analysis?.market_sentiment || 'N/A',
              sub: 'Market mood',
              icon: Activity,
              color: analysisData.current_market_analysis?.market_sentiment === 'bullish' ? '#10B981' : analysisData.current_market_analysis?.market_sentiment === 'bearish' ? '#EF4444' : '#6B7280',
            },
            {
              label: 'Risk Level',
              value: analysisData.risk_level || 'N/A',
              sub: 'Current assessment',
              icon: ShieldCheck,
              color: riskColors[analysisData.risk_level] || '#6B7280',
            },
            {
              label: 'Confidence',
              value: `${Math.round((analysisData.confidence_score || 0) * 100)}%`,
              sub: 'Analysis reliability',
              icon: Target,
              color: '#3B82F6',
            },
          ].map(stat => (
            <div key={stat.label} style={{ background: '#fff', borderRadius: '16px', border: '1px solid var(--color-border)', padding: '18px 22px', boxShadow: '0 1px 6px rgba(0,0,0,0.04)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: `${stat.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <stat.icon size={18} color={stat.color} />
                </div>
                <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{stat.label}</span>
              </div>
              <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.4rem', fontWeight: 800, color: 'var(--color-text-primary)', textTransform: 'capitalize' }}>{stat.value}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>{stat.sub}</div>
            </div>
          ))}
        </div>
      )}

      {/* AI RECOMMENDATION CARD */}
      {analysisData && (
        <div style={{
          background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', borderRadius: '20px',
          padding: '28px 32px', color: '#fff', marginBottom: '20px',
          boxShadow: '0 4px 24px rgba(26,122,64,0.3)',
        }}>
          <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.1rem', fontWeight: 700, margin: '0 0 12px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            🤖 AI Recommendation
          </h3>
          <p style={{ fontSize: '1.05rem', fontWeight: 600, lineHeight: 1.5, margin: '0 0 12px', color: '#E5FFF0' }}>
            {analysisData.selling_recommendation}
          </p>
          <p style={{ fontSize: '0.9rem', lineHeight: 1.5, margin: '0 0 10px', color: 'rgba(255,255,255,0.85)' }}>
            📈 {analysisData.short_term_outlook}
          </p>
          <p style={{ fontSize: '0.85rem', lineHeight: 1.4, margin: 0, color: 'rgba(255,255,255,0.7)' }}>
            🌤️ {analysisData.weather_impact}
          </p>
        </div>
      )}

      {/* NEARBY MARKETS TABLE */}
      {analysisData?.nearby_markets?.length > 0 && (
        <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '24px 28px', marginBottom: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)', overflowX: 'auto' }}>
          <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 20px' }}>
            🏪 Nearby Markets Comparison
          </h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
                {['Market', 'District', 'Modal Price', 'Min Price', 'Max Price'].map(h => (
                  <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, color: 'var(--color-text-secondary)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {analysisData.nearby_markets.map((mkt, i) => (
                <tr key={`${mkt.market_name}-${i}`} style={{
                  borderBottom: '1px solid var(--color-border)',
                  background: i === 0 ? '#F0FDF4' : i % 2 === 0 ? 'transparent' : 'var(--color-bg-primary)',
                }}>
                  <td style={{ padding: '12px 14px', fontWeight: i === 0 ? 700 : 600, color: 'var(--color-text-primary)' }}>
                    {i === 0 && <span style={{ fontSize: '0.7rem', background: '#10B981', color: '#fff', padding: '2px 6px', borderRadius: '4px', marginRight: '6px' }}>BEST</span>}
                    {mkt.market_name}
                  </td>
                  <td style={{ padding: '12px 14px', color: 'var(--color-text-secondary)' }}>{mkt.district}</td>
                  <td style={{ padding: '12px 14px', fontWeight: 700, color: 'var(--color-accent-primary)' }}>₹{mkt.modal_price?.toLocaleString()}</td>
                  <td style={{ padding: '12px 14px', color: 'var(--color-text-secondary)' }}>₹{mkt.min_price?.toLocaleString()}</td>
                  <td style={{ padding: '12px 14px', color: 'var(--color-text-secondary)' }}>₹{mkt.max_price?.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* PRICE TREND CHART */}
      <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '24px 28px', marginBottom: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
            📈 Price Trend
          </h2>
          <div style={{ display: 'flex', gap: '8px' }}>
            {['7D', '30D', '90D'].map((r, i) => (
              <button key={r} style={{
                padding: '4px 12px', borderRadius: '8px', border: '1.5px solid',
                borderColor: i === 1 ? 'var(--color-accent-primary)' : 'var(--color-border)',
                background: i === 1 ? 'var(--color-section-header-bg)' : 'transparent',
                color: i === 1 ? 'var(--color-accent-primary)' : 'var(--color-text-secondary)',
                fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer',
              }}>{r}</button>
            ))}
          </div>
        </div>
        <PriceTrendChart priceData={priceHistory} mspPrice={mspPrice} cropName={selectedCrop} />
      </div>

      {/* MSP TABLE */}
      <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '24px 28px', marginBottom: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)', overflowX: 'auto' }}>
        <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 20px' }}>
          📋 MSP Reference Table
        </h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
              {['Crop', 'MSP (₹/qtl)', 'Status'].map(h => (
                <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, color: 'var(--color-text-secondary)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {mspData.map((row, i) => (
              <tr key={row.crop} style={{ borderBottom: '1px solid var(--color-border)', background: i % 2 === 0 ? 'transparent' : 'var(--color-bg-primary)' }}>
                <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--color-text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '1.1rem' }}>{row.icon}</span> {row.crop}
                </td>
                <td style={{ padding: '12px 14px', color: 'var(--color-text-secondary)' }}>₹{row.msp.toLocaleString()}</td>
                <td style={{ padding: '12px 14px' }}>
                  <span style={{ padding: '3px 10px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 600, background: '#E0F2FE', color: '#0369A1' }}>
                    Official MSP
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* REASONING CARD */}
      {analysisData?.reasoning?.length > 0 && (
        <div style={{ background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', borderRadius: '20px', padding: '28px 32px', color: '#fff' }}>
          <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.1rem', fontWeight: 700, margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            📊 Analysis Reasoning
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            {analysisData.reasoning.map((reason, i) => (
              <div key={i} style={{ display: 'flex', gap: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '12px', padding: '12px 14px' }}>
                <span style={{ color: '#86EFAC', fontWeight: 700, flexShrink: 0 }}>•</span>
                <span style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.9)', lineHeight: 1.5 }}>{reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </PageWrapper>
  );
};

export { MarketPage };
