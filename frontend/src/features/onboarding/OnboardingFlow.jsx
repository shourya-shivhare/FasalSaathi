import React, { useState } from 'react';
import { Check, Leaf, Globe, MapPin, Wheat, ChevronRight } from 'lucide-react';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { useFieldStore } from '../../stores/useFieldStore.jsx';

const LANGUAGES = [
  { code: 'hi', name: 'हिंदी', eng: 'Hindi', flag: '🇮🇳' },
  { code: 'pa', name: 'ਪੰਜਾਬੀ', eng: 'Punjabi', flag: '🇮🇳' },
  { code: 'mr', name: 'मराठी', eng: 'Marathi', flag: '🇮🇳' },
  { code: 'te', name: 'తెలుగు', eng: 'Telugu', flag: '🇮🇳' },
  { code: 'ta', name: 'தமிழ்', eng: 'Tamil', flag: '🇮🇳' },
  { code: 'kn', name: 'ಕನ್ನಡ', eng: 'Kannada', flag: '🇮🇳' },
  { code: 'bn', name: 'বাংলা', eng: 'Bengali', flag: '🇮🇳' },
  { code: 'en', name: 'English', eng: 'English', flag: '🌐' },
];

const CROPS = ['Wheat', 'Rice', 'Cotton', 'Maize', 'Soybean', 'Mustard', 'Gram', 'Sugarcane', 'Sunflower', 'Potato'];

const StepIndicator = ({ current, total }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '0 0 32px' }}>
    {Array.from({ length: total }, (_, i) => (
      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ position: 'relative' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: i < current ? 'rgba(74,222,128,0.2)' : i === current ? '#fff' : 'rgba(255,255,255,0.1)',
            border: i === current ? '2px solid #FACC15' : i < current ? '2px solid #4ADE80' : '2px solid rgba(255,255,255,0.2)',
            color: i < current ? '#4ADE80' : i === current ? '#0F4C2A' : 'rgba(255,255,255,0.4)',
            fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700,
          }}>
            {i < current ? <Check size={16} /> : i + 1}
          </div>
          {i < total - 1 && (
            <div style={{ position: 'absolute', left: '50%', top: '100%', width: '2px', height: '24px', background: i < current ? '#4ADE80' : 'rgba(255,255,255,0.15)', transform: 'translateX(-50%)' }} />
          )}
        </div>
        <div>
          <div style={{ fontWeight: i === current ? 700 : 500, color: i === current ? '#fff' : i < current ? '#86EFAC' : 'rgba(255,255,255,0.5)', fontSize: '0.875rem' }}>
            {['Language', 'Location', 'Crop Setup'][i]}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.4)', marginTop: '1px' }}>
            {['Choose your language', 'Set farm location', 'Add your crops'][i]}
          </div>
        </div>
      </div>
    ))}
  </div>
);

const OnboardingFlow = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const [lang, setLang] = useState('hi');
  const [location, setLocation] = useState('');
  const [state, setState] = useState('');
  const [selectedCrops, setSelectedCrops] = useState([]);
  const [fieldSize, setFieldSize] = useState('');
  const { completeOnboarding } = useUserStore();
  const { addField } = useFieldStore();

  const handleComplete = () => {
    completeOnboarding({ name: 'Farmer', village: location || 'Unknown', state: state || 'Unknown', language: lang });
    if (selectedCrops.length > 0 && fieldSize) {
      addField({ name: 'Main Field', crop: selectedCrops[0], area: fieldSize, areaUnit: 'acres', soilType: 'Loamy', location: { village: location, district: '', state } });
    }
    onComplete();
  };

  const toggleCrop = (crop) => setSelectedCrops(p => p.includes(crop) ? p.filter(c => c !== crop) : [...p, crop]);

  return (
    <div style={{ display: 'flex', minHeight: '100dvh', fontFamily: "'Inter',sans-serif" }}>
      {/* LEFT PANEL */}
      <div style={{ width: '400px', flexShrink: 0, background: 'linear-gradient(160deg,#0A2E18,#0F4C2A,#1A5C30)', display: 'flex', flexDirection: 'column', padding: '48px 40px', position: 'relative', overflow: 'hidden' }}>
        {/* Pattern */}
        <div style={{ position: 'absolute', inset: 0, opacity: 0.05, backgroundImage: 'radial-gradient(circle at 1px 1px, #4ADE80 1px, transparent 0)', backgroundSize: '32px 32px', pointerEvents: 'none' }} />
        {/* Glow */}
        <div style={{ position: 'absolute', bottom: '-20%', right: '-20%', width: '400px', height: '400px', borderRadius: '50%', background: 'radial-gradient(circle,rgba(26,122,64,0.4),transparent 70%)', pointerEvents: 'none' }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '48px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'linear-gradient(135deg,#1A7A40,#FACC15)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(250,204,21,0.3)' }}>
              <Leaf size={20} color="#fff" />
            </div>
            <span style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.2rem', fontWeight: 800, color: '#fff' }}>FasalSaathi</span>
          </div>

          {/* Welcome */}
          <h1 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.8rem', fontWeight: 800, color: '#fff', margin: '0 0 10px', lineHeight: 1.2 }}>
            Welcome to<br />FasalSaathi
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: '0.9rem', margin: '0 0 40px', lineHeight: 1.65 }}>
            Let's set up your farm in just 3 easy steps and start your smart farming journey.
          </p>

          <StepIndicator current={step} total={3} />
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div style={{ flex: 1, background: '#F7F9F5', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '48px' }}>
        <div style={{ width: '100%', maxWidth: '520px' }}>
          {/* Step Badge */}
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#D4EDDA', border: '1px solid #6EE7B7', borderRadius: '20px', padding: '5px 14px', marginBottom: '20px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#1A7A40', display: 'inline-block' }} />
            <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#065F46' }}>Step {step + 1} of 3</span>
          </div>

          {/* STEP 0: LANGUAGE */}
          {step === 0 && (
            <>
              <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.75rem', fontWeight: 800, color: '#1A2B1A', margin: '0 0 6px' }}>Choose Your Language</h2>
              <p style={{ color: '#4A5568', margin: '0 0 28px', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Globe size={15} /> Apni bhasha chuniye
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '32px' }}>
                {LANGUAGES.map(l => {
                  const sel = lang === l.code;
                  return (
                    <button key={l.code} onClick={() => setLang(l.code)} style={{
                      padding: '14px 16px', borderRadius: '14px', border: `2px solid ${sel ? '#1A7A40' : '#E2E8E0'}`,
                      background: sel ? '#D4EDDA' : '#fff', cursor: 'pointer', textAlign: 'left',
                      display: 'flex', alignItems: 'center', gap: '10px', transition: 'all 0.15s',
                    }}>
                      <span style={{ fontSize: '1.2rem' }}>{l.flag}</span>
                      <div>
                        <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: sel ? '#1A7A40' : '#1A2B1A', fontSize: '0.95rem' }}>{l.name}</div>
                        <div style={{ fontSize: '0.72rem', color: '#4A5568' }}>{l.eng}</div>
                      </div>
                      {sel && <Check size={16} color="#1A7A40" style={{ marginLeft: 'auto' }} />}
                    </button>
                  );
                })}
              </div>
            </>
          )}

          {/* STEP 1: LOCATION */}
          {step === 1 && (
            <>
              <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.75rem', fontWeight: 800, color: '#1A2B1A', margin: '0 0 6px' }}>Set Farm Location</h2>
              <p style={{ color: '#4A5568', margin: '0 0 28px', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MapPin size={15} /> Apne kheton ki jagah batayiye
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '32px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#4A5568', display: 'block', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Village / Town</label>
                  <input value={location} onChange={e => setLocation(e.target.value)} placeholder="e.g. Unnao" style={{ width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1.5px solid #E2E8E0', background: '#fff', fontSize: '0.9rem', color: '#1A2B1A', outline: 'none', boxSizing: 'border-box', transition: 'border-color 0.15s' }}
                    onFocus={e => e.target.style.borderColor = '#1A7A40'} onBlur={e => e.target.style.borderColor = '#E2E8E0'} />
                </div>
                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#4A5568', display: 'block', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>State</label>
                  <select value={state} onChange={e => setState(e.target.value)} style={{ width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1.5px solid #E2E8E0', background: '#fff', fontSize: '0.9rem', color: '#1A2B1A', outline: 'none', appearance: 'none', cursor: 'pointer' }}>
                    <option value="">Select State...</option>
                    {['Uttar Pradesh', 'Punjab', 'Haryana', 'Maharashtra', 'Gujarat', 'Rajasthan', 'Madhya Pradesh', 'Bihar', 'West Bengal', 'Karnataka'].map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <button style={{ padding: '13px', borderRadius: '12px', border: '1.5px dashed #1A7A40', background: '#D4EDDA', color: '#1A7A40', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <MapPin size={16} /> Use Current GPS Location
                </button>
              </div>
            </>
          )}

          {/* STEP 2: CROPS */}
          {step === 2 && (
            <>
              <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.75rem', fontWeight: 800, color: '#1A2B1A', margin: '0 0 6px' }}>Crop Setup</h2>
              <p style={{ color: '#4A5568', margin: '0 0 16px', fontSize: '0.9rem' }}>Select your current crops and field size</p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '8px', marginBottom: '20px' }}>
                {CROPS.map(crop => {
                  const sel = selectedCrops.includes(crop);
                  return (
                    <button key={crop} onClick={() => toggleCrop(crop)} style={{
                      padding: '10px 8px', borderRadius: '12px', border: `2px solid ${sel ? '#1A7A40' : '#E2E8E0'}`,
                      background: sel ? '#D4EDDA' : '#fff', cursor: 'pointer', fontWeight: 600, fontSize: '0.82rem',
                      color: sel ? '#1A7A40' : '#4A5568', transition: 'all 0.15s', textAlign: 'center',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px',
                    }}>
                      {sel && <Check size={12} />} {crop}
                    </button>
                  );
                })}
              </div>
              <div style={{ marginBottom: '32px' }}>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#4A5568', display: 'block', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Field Size (Acres)</label>
                <input type="number" value={fieldSize} onChange={e => setFieldSize(e.target.value)} placeholder="e.g. 2.5" style={{ width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1.5px solid #E2E8E0', background: '#fff', fontSize: '0.9rem', color: '#1A2B1A', outline: 'none', boxSizing: 'border-box' }} />
              </div>
            </>
          )}

          {/* Navigation Buttons */}
          <div style={{ display: 'flex', gap: '12px' }}>
            {step > 0 && (
              <button onClick={() => setStep(s => s - 1)} style={{ flex: 1, padding: '14px', borderRadius: '14px', border: '1.5px solid #E2E8E0', background: '#fff', color: '#4A5568', fontWeight: 600, fontSize: '0.95rem', cursor: 'pointer' }}>
                ← Back
              </button>
            )}
            <button
              onClick={step < 2 ? () => setStep(s => s + 1) : handleComplete}
              style={{ flex: step > 0 ? 2 : 1, padding: '14px', borderRadius: '14px', border: 'none', background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', color: '#fff', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', boxShadow: '0 4px 16px rgba(26,122,64,0.3)' }}>
              {step < 2 ? <>Continue <ChevronRight size={18} /></> : '🚀 Start Farming'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export { OnboardingFlow };
