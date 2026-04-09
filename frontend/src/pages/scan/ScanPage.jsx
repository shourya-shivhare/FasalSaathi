import React, { useState, useRef } from 'react';
import { Camera, ScanLine, CheckCircle2, AlertCircle, History, ArrowRight, X, Upload, Info } from 'lucide-react';
import { PageWrapper } from '../../components/layout/PageWrapper';

const ScanPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanDone, setScanDone] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const mockHistory = [
    { id: 1, name: 'Aphids', date: '24 Mar', confidence: 92, color: '#DC2626' },
    { id: 2, name: 'Leaf Blight', date: '20 Mar', confidence: 88, color: '#F59E0B' },
    { id: 3, name: 'Spotted Beetle', date: '15 Mar', confidence: 95, color: '#DC2626' },
  ];

  const handleFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImage(reader.result);
      setScanDone(false);
      setIsScanning(true);
      setTimeout(() => { setIsScanning(false); setScanDone(true); }, 2200);
    };
    reader.readAsDataURL(file);
  };

  const handleInputChange = (e) => handleFile(e.target.files[0]);
  const handleDrop = (e) => { e.preventDefault(); setIsDragging(false); handleFile(e.dataTransfer.files[0]); };
  const clearImage = () => { setSelectedImage(null); setIsScanning(false); setScanDone(false); };

  return (
    <PageWrapper>
      {/* Page Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.65rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
          🔍 Pest Scanner
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: '4px 0 0' }}>
          AI-powered crop health detection using YOLOv8
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '24px', alignItems: 'start' }}>
        {/* LEFT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

          {/* Upload Zone */}
          {!selectedImage ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              style={{
                background: isDragging ? 'var(--color-section-header-bg)' : '#fff',
                border: `2px dashed ${isDragging ? 'var(--color-accent-primary)' : 'var(--color-border)'}`,
                borderRadius: '20px', padding: '56px 32px', textAlign: 'center',
                cursor: 'pointer', transition: 'all 0.2s',
                boxShadow: '0 1px 8px rgba(0,0,0,0.05)',
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--color-accent-primary)'}
              onMouseLeave={e => { if (!isDragging) e.currentTarget.style.borderColor = 'var(--color-border)'; }}
            >
              <div style={{ width: '72px', height: '72px', borderRadius: '50%', background: 'var(--color-section-header-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
                <Camera size={32} color="var(--color-accent-primary)" />
              </div>
              <p style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 8px' }}>
                Apni fasal ki photo lo
              </p>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', margin: '0 0 24px' }}>
                Drag & drop karo ya click kar ke upload karo
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 22px', background: 'var(--color-accent-primary)', color: '#fff', border: 'none', borderRadius: '12px', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}>
                  <Upload size={16} /> Upload Image
                </button>
                <button style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 22px', background: 'transparent', color: 'var(--color-accent-primary)', border: '1.5px solid var(--color-accent-primary)', borderRadius: '12px', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}>
                  <Camera size={16} /> Use Camera
                </button>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--color-border)', marginTop: '16px' }}>Supported: JPG, PNG, WebP</p>
              <input type="file" ref={fileInputRef} onChange={handleInputChange} accept="image/*" style={{ display: 'none' }} />
            </div>
          ) : (
            <div style={{ position: 'relative', borderRadius: '20px', overflow: 'hidden', border: '1px solid var(--color-border)', boxShadow: '0 4px 16px rgba(0,0,0,0.1)' }}>
              <img src={selectedImage} alt="Crop" style={{ width: '100%', maxHeight: '360px', objectFit: 'cover', display: 'block' }} />
              <button onClick={clearImage} style={{ position: 'absolute', top: '12px', right: '12px', width: '36px', height: '36px', borderRadius: '50%', background: 'rgba(0,0,0,0.5)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#fff', backdropFilter: 'blur(8px)' }}>
                <X size={18} />
              </button>
              {isScanning && (
                <div style={{ position: 'absolute', inset: 0, background: 'rgba(15,76,42,0.6)', backdropFilter: 'blur(3px)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px' }}>
                  <div style={{ width: '56px', height: '56px', border: '4px solid rgba(255,255,255,0.2)', borderTopColor: '#4ADE80', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                  <div>
                    <p style={{ color: '#fff', fontWeight: 700, textAlign: 'center', margin: 0 }}>Analyzing Image...</p>
                    <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.8rem', textAlign: 'center', margin: '4px 0 0' }}>YOLOv8 pest detection running</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Detection Result */}
          {scanDone && !isScanning && (
            <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid var(--color-border)', borderLeft: '4px solid var(--color-accent-primary)', padding: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)', animation: 'fadeIn 0.4s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <CheckCircle2 size={22} color="var(--color-accent-primary)" />
                <span style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: 'var(--color-accent-primary)', fontSize: '0.95rem' }}>Detection Complete</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                <div>
                  <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.4rem', fontWeight: 800, color: 'var(--color-text-primary)', margin: '0 0 6px' }}>Aphids (Maahu)</h3>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    <span style={{ background: '#FEF3C7', color: '#92400E', fontSize: '0.78rem', fontWeight: 600, padding: '3px 10px', borderRadius: '20px' }}>87% Confidence</span>
                    <span style={{ background: '#FEE2E2', color: '#DC2626', fontSize: '0.78rem', fontWeight: 600, padding: '3px 10px', borderRadius: '20px' }}>🔴 Medium Severity</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Treatment Plan */}
          {scanDone && (
            <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid var(--color-border)', padding: '24px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
              <h4 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 20px' }}>
                <AlertCircle size={18} color="#F59E0B" /> Treatment Plan
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                {[
                  { label: 'Recommended', value: 'Neem Oil Spray (3%)' },
                  { label: 'Dosage', value: '200ml per acre' },
                  { label: 'Urgency', value: 'Medium', color: '#F59E0B' },
                  { label: 'Best Time', value: 'Early Morning' },
                ].map(item => (
                  <div key={item.label} style={{ background: 'var(--color-bg-primary)', borderRadius: '10px', padding: '12px 14px' }}>
                    <p style={{ fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--color-text-secondary)', margin: '0 0 4px' }}>{item.label}</p>
                    <p style={{ fontWeight: 600, color: item.color || 'var(--color-text-primary)', margin: 0, fontSize: '0.9rem' }}>{item.value}</p>
                  </div>
                ))}
              </div>
              <button style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '13px', background: 'var(--color-accent-primary)', color: '#fff', border: 'none', borderRadius: '12px', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer' }}>
                View Detailed Guide <ArrowRight size={16} />
              </button>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

          {/* Recent Scans */}
          <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 1px 8px rgba(0,0,0,0.05)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <History size={17} color="var(--color-accent-primary)" /> Recent Scans
              </h3>
              <button style={{ fontSize: '0.8rem', color: 'var(--color-accent-primary)', fontWeight: 600, border: 'none', background: 'none', cursor: 'pointer' }}>See All</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {mockHistory.map(scan => (
                <div key={scan.id} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', borderRadius: '12px', background: 'var(--color-bg-primary)', cursor: 'pointer', transition: 'background 0.15s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--color-section-header-bg)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'var(--color-bg-primary)'}>
                  <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: `${scan.color}18`, border: `1.5px solid ${scan.color}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <ScanLine size={16} color={scan.color} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontWeight: 600, color: 'var(--color-text-primary)', margin: 0, fontSize: '0.875rem' }}>{scan.name}</p>
                    <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.75rem', margin: '1px 0 0' }}>{scan.date}</p>
                  </div>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-primary)', background: 'var(--color-section-header-bg)', padding: '3px 8px', borderRadius: '8px', flexShrink: 0 }}>{scan.confidence}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* How it Works */}
          <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 1px 8px rgba(0,0,0,0.05)' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Info size={16} color="var(--color-accent-primary)" /> How It Works
            </h3>
            {[
              { n: 1, title: 'Upload Photo', desc: 'Click a clear image of your affected crop' },
              { n: 2, title: 'AI Analyzes', desc: 'YOLOv8 model detects pest type & severity' },
              { n: 3, title: 'Get Treatment', desc: 'Receive detailed treatment recommendations' },
            ].map(step => (
              <div key={step.n} style={{ display: 'flex', gap: '14px', marginBottom: '14px', alignItems: 'flex-start' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', flexShrink: 0 }}>{step.n}</div>
                <div>
                  <p style={{ fontWeight: 600, color: 'var(--color-text-primary)', margin: '0 0 2px', fontSize: '0.875rem' }}>{step.title}</p>
                  <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.78rem', margin: 0 }}>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Tips */}
          <div style={{ background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', borderRadius: '16px', padding: '20px 22px' }}>
            <h4 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", color: '#fff', fontWeight: 700, fontSize: '0.9rem', margin: '0 0 12px' }}>💡 Tips for Best Results</h4>
            {['Take photo in good natural light', 'Focus clearly on affected leaves', 'Include both healthy & diseased parts', 'Avoid blurry or dark images'].map((tip, i) => (
              <p key={i} style={{ color: 'rgba(255,255,255,0.85)', fontSize: '0.8rem', margin: '0 0 6px', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                <span style={{ color: '#86EFAC', flexShrink: 0 }}>✓</span> {tip}
              </p>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </PageWrapper>
  );
};

export default ScanPage;
