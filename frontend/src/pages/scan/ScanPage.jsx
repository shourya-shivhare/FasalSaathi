import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Camera, ScanLine, CheckCircle2, AlertCircle, ArrowRight, X, Upload, Info, Loader2, MessageCircle } from 'lucide-react';
import { PageWrapper } from '../../components/layout/PageWrapper';
import api from '../../lib/api.jsx';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../../stores/useChatStore.jsx';
import { useUserStore } from '../../stores/useUserStore.jsx';

const SEVERITY_STYLES = {
  High:   { bg: 'var(--color-danger-bg)', text: 'var(--color-danger)', dot: 'var(--color-danger)' },
  Medium: { bg: 'var(--color-warning-bg)', text: 'var(--color-warning-text)', dot: 'var(--color-warning)' },
  Low:    { bg: 'var(--color-success-bg)', text: 'var(--color-success-text)', dot: 'var(--color-success)' },
};


const ScanPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedFile, setSelectedFile]   = useState(null);
  const [isScanning,   setIsScanning]     = useState(false);
  const [scanResult,   setScanResult]     = useState(null);   // API response
  const [scanError,    setScanError]      = useState(null);
  const [isDragging,   setIsDragging]     = useState(false);
  const fileInputRef = useRef(null);

  const navigate = useNavigate();
  const { injectScanContext } = useChatStore();
  const accessToken = useUserStore(state => state.accessToken);



  const handleChatHandoff = () => {
    if (!scanResult) return;
    injectScanContext(scanResult);
    navigate('/chat');
  };



  // ── File selection handlers ────────────────────────────────────────────
  const handleFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    setSelectedFile(file);
    setScanResult(null);
    setScanError(null);
    const reader = new FileReader();
    reader.onloadend = () => setSelectedImage(reader.result);
    reader.readAsDataURL(file);
  };

  const handleInputChange = (e) => handleFile(e.target.files[0]);
  const handleDrop = (e) => { e.preventDefault(); setIsDragging(false); handleFile(e.dataTransfer.files[0]); };
  const clearImage = () => { setSelectedImage(null); setSelectedFile(null); setIsScanning(false); setScanResult(null); setScanError(null); };

  // ── Real scan — calls backend YOLO endpoint ───────────────────────────
  const handleScan = async () => {
    if (!selectedFile || isScanning) return;
    setIsScanning(true);
    setScanResult(null);
    setScanError(null);
    try {
      const result = await api.detectPest(selectedFile, accessToken);
      setScanResult(result);
    } catch (err) {
      setScanError(err.message || 'Detection failed. Please try again.');
    } finally {
      setIsScanning(false);
    }
  };

  // ── Derived helpers ───────────────────────────────────────────────────
  const topDetection = scanResult?.results?.[0] || null;
  const hasPests     = scanResult?.total > 0;

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

        {/* ── LEFT COLUMN ─────────────────────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

          {/* Upload Zone */}
          {!selectedImage ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              style={{
                background: isDragging ? 'var(--color-section-header-bg)' : 'var(--color-bg-secondary)',
                border: `2px dashed ${isDragging ? 'var(--color-accent-primary)' : 'var(--color-border)'}`,
                borderRadius: '20px', padding: '56px 32px', textAlign: 'center',
                cursor: 'pointer', transition: 'all 0.2s',
                boxShadow: '0 1px 8px rgba(0,0,0,0.04)',
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
                Drag &amp; drop karo ya click kar ke upload karo
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 22px', background: 'var(--color-accent-primary)', color: '#fff', border: 'none', borderRadius: '12px', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}>
                  <Upload size={16} /> Upload Image
                </button>
                <button
                  style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 22px', background: 'transparent', color: 'var(--color-accent-primary)', border: '1.5px solid var(--color-accent-primary)', borderRadius: '12px', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}
                  onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
                >
                  <Camera size={16} /> Use Camera
                </button>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--color-border)', marginTop: '16px' }}>Supported: JPG, PNG, WebP</p>
              <input type="file" ref={fileInputRef} onChange={handleInputChange} accept="image/*" capture="environment" style={{ display: 'none' }} />
            </div>
          ) : (
            /* Image Preview + Scan Button */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
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

              {/* Scan Action Button */}
              {!scanResult && !scanError && (
                <button
                  onClick={handleScan}
                  disabled={isScanning}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                    padding: '14px', background: isScanning ? 'var(--color-border)' : 'linear-gradient(135deg, var(--sidebar-bg), var(--color-accent-primary))',
                    color: '#fff', border: 'none', borderRadius: '14px', fontWeight: 700,
                    fontSize: '1rem', cursor: isScanning ? 'not-allowed' : 'pointer',
                    boxShadow: isScanning ? 'none' : '0 4px 16px rgba(26,122,64,0.3)',
                    transition: 'all 0.2s',
                  }}
                >
                  {isScanning ? <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} /> : <ScanLine size={20} />}
                  {isScanning ? 'Scanning...' : '🔍 Scan for Pests'}
                </button>
              )}
            </div>
          )}

          {/* ── Error State ──────────────────────────────────────────── */}
          {scanError && (
            <div style={{ background: 'var(--color-danger-bg)', borderRadius: '14px', border: '1px solid var(--color-danger)', borderLeft: '4px solid var(--color-danger)', padding: '16px 20px', animation: 'fadeIn 0.3s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <AlertCircle size={20} color="var(--color-danger)" />
                <span style={{ fontWeight: 700, color: 'var(--color-danger)' }}>Detection Failed</span>
              </div>
              <p style={{ color: 'var(--color-text-primary)', fontSize: '0.875rem', margin: '0 0 12px' }}>{scanError}</p>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.8rem', margin: 0 }}>
                💡 Make sure the backend server is running: <code style={{ background: 'var(--color-danger-bg)', padding: '2px 6px', borderRadius: '6px' }}>cd backend && uvicorn main:app --port 8000</code>
              </p>
            </div>
          )}

          {/* ── No detections ─────────────────────────────────────────── */}
          {scanResult && !hasPests && (
            <div style={{ background: 'var(--color-success-bg)', borderRadius: '14px', border: '1px solid var(--color-success)', borderLeft: '4px solid var(--color-success)', padding: '20px', animation: 'fadeIn 0.4s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <CheckCircle2 size={22} color="var(--color-success)" />
                <div>
                  <p style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: 'var(--color-success-text)', margin: 0 }}>Fasal Swasth Hai! 🌿</p>
                  <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem', margin: '4px 0 0' }}>No pests detected in the uploaded image.</p>
                </div>
              </div>
            </div>
          )}

          {/* ── Detection Result ──────────────────────────────────────── */}
          {hasPests && (
            <div style={{ background: 'var(--color-bg-secondary)', borderRadius: '16px', border: '1px solid var(--color-border)', borderLeft: '4px solid var(--color-accent-primary)', padding: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.04)', animation: 'fadeIn 0.4s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <CheckCircle2 size={22} color="var(--color-accent-primary)" />
                <span style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: 'var(--color-accent-primary)', fontSize: '0.95rem' }}>
                  {scanResult.total} Pest{scanResult.total > 1 ? 's' : ''} Detected
                </span>
              </div>
              {scanResult.results.map((det, i) => {
                const sevRaw = det.severity || 'Medium';
                const sev = sevRaw.replace(/[🔴🟡🟢]\s*/g, '').trim();
                const style = SEVERITY_STYLES[sev] || SEVERITY_STYLES.Medium;
                return (
                  <div key={i} style={{ marginBottom: i < scanResult.results.length - 1 ? '12px' : 0 }}>
                    <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-text-primary)', margin: '0 0 8px' }}>
                      {det.pest || det.class}
                    </h3>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{ background: style.bg, color: style.text, fontSize: '0.78rem', fontWeight: 600, padding: '3px 10px', borderRadius: '20px' }}>
                        ● {sev} Severity
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* ── Treatment Plan ────────────────────────────────────────── */}
          {hasPests && scanResult.suggestions?.length > 0 && (
            <div style={{ background: 'var(--color-bg-secondary)', borderRadius: '16px', border: '1px solid var(--color-border)', padding: '24px', boxShadow: '0 2px 12px rgba(0,0,0,0.04)' }}>
              <h4 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 16px' }}>
                <AlertCircle size={18} color="var(--color-warning)" /> Treatment Recommendations
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {scanResult.suggestions.map((tip, i) => (
                  <div key={i} style={{ display: 'flex', gap: '10px', padding: '12px 14px', background: 'var(--color-bg-primary)', borderRadius: '10px', border: '1px solid var(--color-border)' }}>
                    <span style={{ color: 'var(--color-accent-primary)', fontWeight: 700, flexShrink: 0 }}>✓</span>
                    <span style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)', lineHeight: 1.5 }}>{tip}</span>
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '20px' }}>
                <button
                  onClick={handleChatHandoff}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '13px', background: 'var(--color-bg-secondary)', color: 'var(--color-accent-primary)', border: '2px solid var(--color-accent-primary)', borderRadius: '12px', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 4px 12px rgba(26,122,64,0.05)' }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'var(--color-section-header-bg)'; e.currentTarget.style.transform = 'translateY(-1px)'; }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'var(--color-bg-secondary)'; e.currentTarget.style.transform = 'none'; }}
                >
                  <MessageCircle size={18} /> Chat with AI Expert about this
                </button>
                <button
                  onClick={clearImage}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '13px', background: 'transparent', color: 'var(--color-text-secondary)', border: 'none', borderRadius: '12px', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer', transition: 'all 0.2s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--color-surface-hover)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  Scan Another Image <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ── RIGHT COLUMN ──────────────────────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>



          {/* How it Works */}
          <div style={{ background: 'var(--color-bg-secondary)', borderRadius: '16px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 1px 8px rgba(0,0,0,0.04)' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Info size={16} color="var(--color-accent-primary)" /> How It Works
            </h3>
            {[
              { n: 1, title: 'Upload Photo', desc: 'Click a clear image of your affected crop' },
              { n: 2, title: 'AI Analyzes', desc: 'YOLOv8 model detects pest type & severity' },
              { n: 3, title: 'Get Treatment', desc: 'Receive detailed treatment recommendations' },
            ].map(step => (
              <div key={step.n} style={{ display: 'flex', gap: '14px', marginBottom: '14px', alignItems: 'flex-start' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--sidebar-bg), var(--color-accent-primary))', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', flexShrink: 0 }}>{step.n}</div>
                <div>
                  <p style={{ fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 2px', fontSize: '0.875rem' }}>{step.title}</p>
                  <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.78rem', margin: 0 }}>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Tips */}
          <div style={{ background: 'linear-gradient(135deg, var(--sidebar-bg), var(--color-accent-primary))', borderRadius: '16px', padding: '20px 22px' }}>
            <h4 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", color: '#fff', fontWeight: 700, fontSize: '0.9rem', margin: '0 0 12px' }}>💡 Tips for Best Results</h4>
            {['Take photo in good natural light', 'Focus clearly on affected leaves', 'Include both healthy & diseased parts', 'Avoid blurry or dark images'].map((tip, i) => (
              <p key={i} style={{ color: 'rgba(255,255,255,0.85)', fontSize: '0.8rem', margin: '0 0 6px', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                <span style={{ color: 'var(--color-accent-secondary)', flexShrink: 0 }}>✓</span> {tip}
              </p>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin    { to { transform: rotate(360deg); } }
        @keyframes fadeIn  { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </PageWrapper>
  );
};

export default ScanPage;
