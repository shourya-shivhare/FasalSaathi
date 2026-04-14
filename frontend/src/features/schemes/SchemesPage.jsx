import React, { useState, useEffect } from 'react';
import {
  Landmark, Search, Filter, ExternalLink, ChevronDown,
  ChevronUp, Award, Loader2, AlertTriangle, Sprout,
} from 'lucide-react';
import api from '../../lib/api';
import { useUserStore } from '../../stores/useUserStore';
import { useChatStore } from '../../stores/useChatStore.jsx';

// ── Indian states list ──────────────────────────────────────────────────────
const STATES = [
  'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh',
  'Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka',
  'Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram',
  'Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu',
  'Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal','Delhi',
];

const CATEGORIES = ['marginal', 'small', 'semi-medium', 'medium', 'large'];

export const SchemesPage = () => {
  const farmer = useUserStore((s) => s.farmer);
  const accessToken = useUserStore((s) => s.accessToken);

  // Form state — pre-filled from profile
  const [state, setState] = useState(farmer?.state || '');
  const [district, setDistrict] = useState(farmer?.district || '');
  const [category, setCategory] = useState(farmer?.category || 'marginal');
  const [age, setAge] = useState(farmer?.age || '');
  const [gender, setGender] = useState(farmer?.gender || '');
  const [income, setIncome] = useState(farmer?.annual_income || '');
  const [crops, setCrops] = useState(farmer?.crops_grown || '');

  const previousSchemes = useChatStore((s) => s.analysisContext?.schemes);

  // Results
  const [schemes, setSchemes] = useState(previousSchemes?.matched_schemes || []);
  const [summary, setSummary] = useState(previousSchemes?.farmer_summary || '');
  const [totalFound, setTotalFound] = useState(previousSchemes?.total_found || 0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [hasSearched, setHasSearched] = useState(!!previousSchemes);

  const handleSearch = async () => {
    if (!state) { setError('Please select a state'); return; }
    setLoading(true);
    setError(null);
    setSchemes([]);
    setHasSearched(true);
    try {
      const payload = {
        state,
        district: district || undefined,
        farmer_category: category,
        crop_types: crops ? crops.split(',').map(c => c.trim()).filter(Boolean) : [],
        annual_income: income ? parseInt(income) : undefined,
        gender: gender || undefined,
        age: age ? parseInt(age) : undefined,
      };
      const data = await api.getSchemeRecommendation(payload, accessToken);
      setSchemes(data.matched_schemes || []);
      setSummary(data.farmer_summary || '');
      setTotalFound(data.total_found || 0);

      // Share context with Chatbot
      useChatStore.getState().setAnalysisContext({ scheme_recommendations: data });
    } catch (err) {
      setError(err.message || 'Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => {
    if (score >= 0.8) return '#22c55e';
    if (score >= 0.5) return '#f59e0b';
    return '#ef4444';
  };

  const scoreLabel = (score) => {
    if (score >= 0.8) return 'Highly Eligible';
    if (score >= 0.5) return 'Likely Eligible';
    return 'May Qualify';
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

  return (
    <div style={pageStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div style={{
          width: '44px', height: '44px', borderRadius: '12px',
          background: 'linear-gradient(135deg, #1A7A40, #2D8F55)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 16px rgba(26,122,64,0.4)',
        }}>
          <Landmark size={22} color="#fff" />
        </div>
        <h1 style={h1Style}>Government Schemes</h1>
      </div>
      <p style={subtitleStyle}>
        AI-powered recommendations for government schemes you may be eligible for
      </p>

      {/* Filter Form */}
      <div style={{
        background: 'rgba(255,255,255,0.04)', backdropFilter: 'blur(12px)',
        border: '1px solid rgba(255,255,255,0.08)', borderRadius: '20px',
        padding: '24px', marginBottom: '28px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '18px' }}>
          <Filter size={16} color="#4ADE80" />
          <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Your Profile</span>
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
            <label style={labelStyle}>Farmer Category</label>
            <select value={category} onChange={e => setCategory(e.target.value)} style={inputStyle}>
              {CATEGORIES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase()+c.slice(1)}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Age</label>
            <input type="number" value={age} onChange={e => setAge(e.target.value)}
              placeholder="e.g. 35" style={inputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Gender</label>
            <select value={gender} onChange={e => setGender(e.target.value)} style={inputStyle}>
              <option value="">Any</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>
          <div>
            <label style={labelStyle}>Annual Income (₹)</label>
            <input type="number" value={income} onChange={e => setIncome(e.target.value)}
              placeholder="e.g. 120000" style={inputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Crops (comma-separated)</label>
            <input value={crops} onChange={e => setCrops(e.target.value)}
              placeholder="e.g. Wheat, Rice" style={inputStyle} />
          </div>
        </div>

        <button onClick={handleSearch} disabled={loading} style={{
          ...btnStyle, opacity: loading ? 0.7 : 1,
          cursor: loading ? 'not-allowed' : 'pointer',
        }}>
          {loading ? <><Loader2 size={18} className="spin" /> Analyzing...</>
            : <><Search size={18} /> Find Eligible Schemes</>}
        </button>
      </div>

      {/* Error */}
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

      {/* Summary bar */}
      {hasSearched && !loading && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '12px 18px', borderRadius: '12px',
          background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.15)',
          marginBottom: '20px', fontSize: '0.85rem', color: 'rgba(255,255,255,0.7)',
        }}>
          <Award size={16} color="#4ADE80" />
          {totalFound > 0
            ? <span><strong style={{ color: '#4ADE80' }}>{totalFound}</strong> schemes matched. {summary}</span>
            : <span>No schemes matched your profile. Try adjusting your filters.</span>
          }
        </div>
      )}

      {/* Results */}
      {schemes.map((s, i) => (
        <div key={i} style={cardStyle}
          onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(74,222,128,0.3)'}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <Sprout size={18} color="#4ADE80" />
                <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
                  {s.scheme_name}
                </h3>
              </div>
              <p style={{ margin: '0 0 4px', fontSize: '0.8rem', color: 'rgba(255,255,255,0.45)' }}>
                {s.ministry}
              </p>
            </div>
            {/* Score badge */}
            <div style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px',
              padding: '8px 14px', borderRadius: '12px',
              background: `${scoreColor(s.eligibility_score)}15`,
              border: `1px solid ${scoreColor(s.eligibility_score)}30`,
              minWidth: '90px',
            }}>
              <span style={{ fontSize: '1.2rem', fontWeight: 800, color: scoreColor(s.eligibility_score) }}>
                {Math.round(s.eligibility_score * 100)}%
              </span>
              <span style={{ fontSize: '0.7rem', color: scoreColor(s.eligibility_score), fontWeight: 600 }}>
                {scoreLabel(s.eligibility_score)}
              </span>
            </div>
          </div>

          {/* Always visible: why recommended */}
          <p style={{
            margin: '12px 0 0', padding: '10px 14px', borderRadius: '10px',
            background: 'rgba(74,222,128,0.06)', fontSize: '0.88rem',
            color: 'rgba(255,255,255,0.8)', lineHeight: 1.5,
          }}>
            {s.why_recommended}
          </p>

          {/* Expand/collapse */}
          <button onClick={() => setExpandedId(expandedId === i ? null : i)}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              background: 'none', border: 'none', color: '#4ADE80',
              cursor: 'pointer', fontSize: '0.82rem', fontWeight: 600,
              marginTop: '10px', padding: 0,
            }}>
            {expandedId === i ? <><ChevronUp size={14} /> Less details</> : <><ChevronDown size={14} /> More details</>}
          </button>

          {expandedId === i && (
            <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <p style={{ margin: '0 0 8px', fontSize: '0.85rem', color: 'rgba(255,255,255,0.7)' }}>
                <strong style={{ color: 'rgba(255,255,255,0.9)' }}>Benefits:</strong> {s.benefits}
              </p>
              {s.category_tags?.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '10px' }}>
                  {s.category_tags.map((t, j) => (
                    <span key={j} style={{
                      padding: '4px 10px', borderRadius: '20px', fontSize: '0.72rem',
                      background: 'rgba(74,222,128,0.1)', color: '#4ADE80', fontWeight: 600,
                    }}>{t}</span>
                  ))}
                </div>
              )}
              {s.apply_url && (
                <a href={s.apply_url} target="_blank" rel="noopener noreferrer" style={{
                  display: 'inline-flex', alignItems: 'center', gap: '6px',
                  padding: '8px 16px', borderRadius: '10px',
                  background: 'rgba(74,222,128,0.12)', color: '#4ADE80',
                  textDecoration: 'none', fontSize: '0.85rem', fontWeight: 600,
                  border: '1px solid rgba(74,222,128,0.2)', transition: 'all 0.15s',
                }}>
                  <ExternalLink size={14} /> Apply / Learn More
                </a>
              )}
            </div>
          )}
        </div>
      ))}

      {/* Spinning animation */}
      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }
      `}</style>
    </div>
  );
};
