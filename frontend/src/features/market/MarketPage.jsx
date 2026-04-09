import React, { useState } from 'react';
import { TrendingUp, TrendingDown, RefreshCw, MapPin, BarChart2, ArrowUpRight, Target } from 'lucide-react';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { PriceTrendChart } from './components/PriceTrendChart';
import { useFieldStore } from '../../stores/useFieldStore.jsx';
import { mockMandiPrices, mockMSPPrices } from '../../lib/mockData.jsx';

const mspData = [
  { crop: 'Wheat',    msp: 2275, market: 3040, icon: '🌾' },
  { crop: 'Rice',     msp: 2183, market: 2050, icon: '🍚' },
  { crop: 'Soybean',  msp: 4600, market: 4820, icon: '🫘' },
  { crop: 'Cotton',   msp: 6620, market: 7100, icon: '🌿' },
  { crop: 'Maize',    msp: 2090, market: 1980, icon: '🌽' },
  { crop: 'Mustard',  msp: 5650, market: 5900, icon: '🌻' },
  { crop: 'Gram',     msp: 5440, market: 5200, icon: '🫛' },
  { crop: 'Sunflower',msp: 6760, market: 6500, icon: '🌸' },
];

const generate30Day = () => {
  const data = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date(); d.setDate(d.getDate() - i);
    const price = Math.round(2900 + Math.sin(i * 0.3) * 200 + Math.random() * 100);
    data.push({ date: d.toISOString().split('T')[0], price, volume: Math.round(800 + Math.random() * 600) });
  }
  return data;
};

const MarketPage = () => {
  const { getActiveField } = useFieldStore();
  const activeField = getActiveField();
  const currentCrop = activeField?.crop || 'Wheat';
  const currentPrice = 3040;
  const mspPrice = 2275;
  const diff = currentPrice - mspPrice;
  const priceHistory = generate30Day();

  return (
    <PageWrapper>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.65rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
            Market Prices
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: '4px 0 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={14} /> Narela Mandi · Updated 2 hrs ago
          </p>
        </div>
        <button style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', border: '1.5px solid var(--color-border)', borderRadius: '12px', background: '#fff', color: 'var(--color-accent-primary)', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}>
          <RefreshCw size={15} /> Refresh
        </button>
      </div>

      {/* HERO PRICE CARD */}
      <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', borderLeft: '5px solid #FACC15', padding: '28px 32px', marginBottom: '20px', boxShadow: '0 4px 20px rgba(0,0,0,0.07)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: 'linear-gradient(135deg,#FEF3C7,#FDE68A)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', flexShrink: 0 }}>🌾</div>
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>Current Mandi Price</div>
            <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-accent-primary)', lineHeight: 1.1 }}>₹{currentPrice.toLocaleString()}</div>
            <div style={{ fontWeight: 600, color: 'var(--color-text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>{currentCrop} (Gehun) · per quintal</div>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', alignItems: 'flex-end' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: diff > 0 ? '#D1FAE5' : '#FEE2E2', borderRadius: '12px', padding: '8px 16px' }}>
            {diff > 0 ? <ArrowUpRight size={18} color="#065F46" /> : <TrendingDown size={18} color="#DC2626" />}
            <span style={{ fontWeight: 700, color: diff > 0 ? '#065F46' : '#DC2626', fontSize: '0.95rem' }}>
              ₹{Math.abs(diff)} {diff > 0 ? 'above' : 'below'} MSP
            </span>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={13} />Narela Mandi · 5 km away
          </div>
        </div>
      </div>

      {/* MINI STATS ROW */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '20px' }}>
        {[
          { label: 'MSP Rate', value: `₹${mspPrice}`, sub: 'Min Support Price', icon: Target, color: '#8B5CF6' },
          { label: '7-Day Change', value: '+₹120', sub: 'vs last week', icon: TrendingUp, color: '#10B981' },
          { label: 'Avg Volume', value: '1,240 Q', sub: 'Quintals/day', icon: BarChart2, color: '#3B82F6' },
        ].map(stat => (
          <div key={stat.label} style={{ background: '#fff', borderRadius: '16px', border: '1px solid var(--color-border)', padding: '18px 22px', boxShadow: '0 1px 6px rgba(0,0,0,0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: `${stat.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <stat.icon size={18} color={stat.color} />
              </div>
              <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{stat.label}</span>
            </div>
            <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.4rem', fontWeight: 800, color: 'var(--color-text-primary)' }}>{stat.value}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>{stat.sub}</div>
          </div>
        ))}
      </div>

      {/* PRICE TREND CHART */}
      <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '24px 28px', marginBottom: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
            📈 30-Day Price Trend
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
        <PriceTrendChart priceData={priceHistory} mspPrice={mspPrice} cropName={currentCrop} />
      </div>

      {/* MSP TABLE */}
      <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '24px 28px', marginBottom: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)', overflowX: 'auto' }}>
        <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 20px' }}>
          📋 MSP Reference Table
        </h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
              {['Crop', 'MSP (₹/qtl)', 'Market Price', 'Difference', 'Status'].map(h => (
                <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, color: 'var(--color-text-secondary)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {mspData.map((row, i) => {
              const d = row.market - row.msp;
              const above = d >= 0;
              return (
                <tr key={row.crop} style={{ borderBottom: '1px solid var(--color-border)', background: i % 2 === 0 ? 'transparent' : 'var(--color-bg-primary)', transition: 'background 0.12s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--color-section-header-bg)'}
                  onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? 'transparent' : 'var(--color-bg-primary)'}>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--color-text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '1.1rem' }}>{row.icon}</span> {row.crop}
                  </td>
                  <td style={{ padding: '12px 14px', color: 'var(--color-text-secondary)' }}>₹{row.msp.toLocaleString()}</td>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--color-text-primary)' }}>₹{row.market.toLocaleString()}</td>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: above ? '#065F46' : '#DC2626' }}>
                    {above ? '+' : ''}₹{d.toLocaleString()}
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <span style={{ padding: '3px 10px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 600, background: above ? '#D1FAE5' : '#FEE2E2', color: above ? '#065F46' : '#DC2626' }}>
                      {above ? '↑ Above MSP' : '↓ Below MSP'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* INSIGHTS CARD */}
      <div style={{ background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', borderRadius: '20px', padding: '28px 32px', color: '#fff' }}>
        <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.1rem', fontWeight: 700, margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          📊 Market Insights
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          {[
            `${currentCrop} prices are ₹${diff} above MSP this week`,
            'Prices show an upward 📈 trend over the past month',
            'Trading volume has been increasing recently',
            'Best sell window: Next 2 weeks before harvest season',
          ].map((insight, i) => (
            <div key={i} style={{ display: 'flex', gap: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '12px', padding: '12px 14px' }}>
              <span style={{ color: '#86EFAC', fontWeight: 700, flexShrink: 0 }}>•</span>
              <span style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.9)', lineHeight: 1.5 }}>{insight}</span>
            </div>
          ))}
        </div>
      </div>
    </PageWrapper>
  );
};

export { MarketPage };
