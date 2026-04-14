import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ScanLine, ArrowRight, ChevronDown, ChevronUp, AlertTriangle, Sun } from 'lucide-react';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { useFieldStore } from '../../stores/useFieldStore.jsx';
import { mockPestAlerts, mockSchemes } from '../../lib/mockData.jsx';

const severityConfig = {
  high:   { bg: '#FEE2E2', border: '#FECACA', text: '#DC2626', label: 'High Risk' },
  medium: { bg: '#FEF3C7', border: '#FCD34D', text: '#92400E', label: 'Medium Risk' },
  low:    { bg: '#D1FAE5', border: '#6EE7B7', text: '#065F46', label: 'Low Risk' },
};

const growthStages = ['Germination', 'Tillering', 'Jointing', 'Heading', 'Harvest'];

const AdvisoryPage = () => {
  const navigate = useNavigate();
  const { getActiveField } = useFieldStore();
  const activeField = getActiveField();
  const [expandedSchemeId, setExpandedSchemeId] = useState(null);
  const [activeStage] = useState(1); // Tillering

  const pestAlerts = mockPestAlerts?.slice(0, 3) || [
    { id: 1, name: 'Aphids (Maahu)', severity: 'high', crop: 'Wheat', region: 'North Punjab', treatment: 'Imidacloprid 0.5ml/L spray' },
    { id: 2, name: 'Yellow Rust', severity: 'medium', crop: 'Wheat', region: 'Haryana, UP', treatment: 'Propiconazole 1ml/L' },
    { id: 3, name: 'Stem Borer', severity: 'low', crop: 'Rice', region: 'West Bengal', treatment: 'Chlorpyrifos 2ml/L' },
  ];

  const schemes = mockSchemes?.slice(0, 3) || [
    { id: '1', name: 'PM-KISAN', benefit: '₹6,000/yr direct benefit', eligibility: 'All small & marginal farmers', description: 'Direct income support to farmer families. Amount is transferred in 3 installments of ₹2,000 each.' },
    { id: '2', name: 'PMFBY Insurance', benefit: 'Crop loss coverage up to 90%', eligibility: 'All loanee & non-loanee farmers', description: 'Provides financial support to farmers suffering crop loss due to natural calamities, pests & diseases.' },
    { id: '3', name: 'Kisan Credit Card', benefit: 'Up to ₹3 lakh at 4% interest', eligibility: 'All farmers with land records', description: 'Short-term credit for crop cultivation, post-harvest expenses, and maintenance of farm assets.' },
  ];

  return (
    <PageWrapper>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.65rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
          Advisory
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: '4px 0 0' }}>
          {activeField ? `${activeField.crop} crop guidance · Your region` : 'Farming guidance & government schemes'}
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '24px', alignItems: 'start' }}>
        {/* LEFT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

          {/* Crop Calendar */}
          <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '24px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
            <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🌾 Crop Calendar — {activeField?.crop || 'Wheat'}
            </h2>
            {/* Timeline */}
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px', position: 'relative' }}>
              {growthStages.map((stage, i) => (
                <React.Fragment key={stage}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, position: 'relative', zIndex: 1 }}>
                    <div style={{
                      width: '36px', height: '36px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem',
                      background: i <= activeStage ? 'var(--color-accent-primary)' : 'var(--color-border)',
                      color: i <= activeStage ? '#fff' : 'var(--color-text-secondary)',
                      border: i === activeStage ? '3px solid #FACC15' : 'none',
                      boxShadow: i === activeStage ? '0 0 0 4px rgba(250,204,21,0.2)' : 'none',
                      transition: 'all 0.2s',
                    }}>{i + 1}</div>
                    <span style={{ fontSize: '0.7rem', marginTop: '8px', textAlign: 'center', fontWeight: i === activeStage ? 700 : 400, color: i <= activeStage ? 'var(--color-accent-primary)' : 'var(--color-text-secondary)' }}>{stage}</span>
                    {i === activeStage && <span style={{ fontSize: '0.65rem', background: 'var(--color-section-header-bg)', color: 'var(--color-accent-primary)', borderRadius: '8px', padding: '1px 6px', marginTop: '2px', fontWeight: 600 }}>Active</span>}
                  </div>
                  {i < growthStages.length - 1 && (
                    <div style={{ flex: 1, height: '3px', background: i < activeStage ? 'var(--color-accent-primary)' : 'var(--color-border)', margin: '0 -8px', marginBottom: '28px', zIndex: 0, flexShrink: 1, maxWidth: '60px' }} />
                  )}
                </React.Fragment>
              ))}
            </div>
            <div style={{ background: 'var(--color-section-header-bg)', borderRadius: '12px', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.1rem' }}>💡</span>
              <span style={{ fontSize: '0.85rem', color: 'var(--color-accent-primary)', fontWeight: 600 }}>
                Next action: Apply second dose of nitrogen fertilizer (urea 50kg/acre)
              </span>
            </div>
          </div>

          {/* Pest Alerts */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                🐛 Pest Alerts
              </h2>
            </div>

            {/* Scan CTA Banner */}
            <div onClick={() => navigate('/detect')} style={{ background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', borderRadius: '16px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', marginBottom: '14px', transition: 'transform 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseLeave={e => e.currentTarget.style.transform = ''}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <ScanLine size={22} color="#fff" />
                </div>
                <div>
                  <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: '#fff', fontSize: '0.95rem' }}>Fasal mein keede?</div>
                  <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.8rem' }}>Apni fasal scan karein aur upchar payein</div>
                </div>
              </div>
              <button style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.2)', border: '1.5px solid rgba(255,255,255,0.4)', borderRadius: '20px', padding: '7px 16px', color: '#fff', fontWeight: 600, fontSize: '0.82rem', cursor: 'pointer', whiteSpace: 'nowrap' }}>
                Scan Now <ArrowRight size={14} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {pestAlerts.map(alert => {
                const s = severityConfig[alert.severity] || severityConfig.medium;
                return (
                  <div key={alert.id} style={{ background: '#fff', borderRadius: '16px', border: `1px solid ${s.border}`, borderLeft: `4px solid ${s.text}`, padding: '16px 20px', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '0.95rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <AlertTriangle size={16} color={s.text} /> {alert.name}
                      </h3>
                      <span style={{ background: s.bg, color: s.text, fontSize: '0.72rem', fontWeight: 700, padding: '3px 10px', borderRadius: '20px' }}>{s.label}</span>
                    </div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', margin: '0 0 6px' }}>
                      📍 Affected: {alert.region || 'North Punjab, Haryana'}
                    </p>
                    <p style={{ fontSize: '0.82rem', color: 'var(--color-text-primary)', margin: 0, fontWeight: 500 }}>
                      💊 Treatment: {alert.treatment}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Government Schemes */}
          <div>
            <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              📜 Government Schemes
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {schemes.map(scheme => {
                const isOpen = expandedSchemeId === scheme.id;
                return (
                  <div key={scheme.id} style={{ background: '#fff', borderRadius: '16px', border: '1px solid var(--color-border)', overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
                    <button onClick={() => setExpandedSchemeId(isOpen ? null : scheme.id)} style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left' }}>
                      <div>
                        <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: 'var(--color-text-primary)', fontSize: '0.95rem' }}>{scheme.name}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--color-accent-primary)', fontWeight: 500, marginTop: '2px' }}>{scheme.benefit}</div>
                      </div>
                      <div style={{ flexShrink: 0, color: 'var(--color-text-secondary)' }}>
                        {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                      </div>
                    </button>
                    {isOpen && (
                      <div style={{ padding: '0 20px 16px', borderTop: '1px solid var(--color-border)' }}>
                        <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', margin: '12px 0 8px', lineHeight: 1.6 }}>{scheme.description}</p>
                        <div style={{ display: 'flex', gap: '10px' }}>
                          <span style={{ background: 'var(--color-section-header-bg)', color: 'var(--color-accent-primary)', fontSize: '0.75rem', fontWeight: 600, padding: '4px 12px', borderRadius: '8px' }}>
                            ✅ You may be eligible
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', position: 'sticky', top: '24px' }}>
          {/* Weather Advisory */}
          <div style={{ background: '#FEF3C7', border: '1.5px solid #FCD34D', borderRadius: '20px', padding: '22px' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: '#92400E', fontSize: '0.95rem', margin: '0 0 14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sun size={18} color="#F59E0B" /> Weather Advisory
            </h3>
            {[
              'High temperature expected in next 48 hours',
              'Consider afternoon irrigation to protect crops',
              'Monitor heat stress in young plants',
              'Avoid fertilizer during peak heat hours (12–3pm)',
            ].map((tip, i) => (
              <div key={i} style={{ display: 'flex', gap: '8px', marginBottom: '10px', alignItems: 'flex-start' }}>
                <span style={{ fontWeight: 700, color: '#F59E0B', flexShrink: 0, fontSize: '0.9rem' }}>•</span>
                <span style={{ fontSize: '0.83rem', color: '#78350F', lineHeight: 1.5 }}>{tip}</span>
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '22px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: 'var(--color-text-primary)', fontSize: '0.95rem', margin: '0 0 16px' }}>
              Quick Actions
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <button onClick={() => navigate('/detect')} style={{ width: '100%', padding: '12px', borderRadius: '12px', border: 'none', background: 'var(--color-accent-primary)', color: '#fff', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <ScanLine size={16} /> Scan for Pests
              </button>
              <button onClick={() => navigate('/chat')} style={{ width: '100%', padding: '12px', borderRadius: '12px', border: '1.5px solid var(--color-accent-primary)', background: 'transparent', color: 'var(--color-accent-primary)', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                💬 Chat with AI Advisor
              </button>
            </div>
          </div>

          {/* Seasonal Tips */}
          <div style={{ background: 'linear-gradient(135deg,#0F4C2A,#1A7A40)', borderRadius: '20px', padding: '22px' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: '#fff', fontSize: '0.9rem', margin: '0 0 14px' }}>
              🌱 Seasonal Tips
            </h3>
            {['Apply potash fertilizer at jointing stage', 'Maintain optimal soil moisture (60–70%)', 'Check for yellow rust every 3 days', 'Pre-harvest quality check recommended'].map((tip, i) => (
              <div key={i} style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                <span style={{ color: '#86EFAC', flexShrink: 0 }}>✓</span>
                <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.85)', lineHeight: 1.5 }}>{tip}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageWrapper>
  );
};

export { AdvisoryPage };
