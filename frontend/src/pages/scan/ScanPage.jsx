import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Camera, ScanLine, CheckCircle2, AlertCircle, History, ArrowRight, X, Upload, Info, Loader2, MessageCircle, Trash2 } from 'lucide-react';
import { PageWrapper } from '../../components/layout/PageWrapper';
import api from '../../lib/api.jsx';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../../stores/useChatStore.jsx';

const SEVERITY_STYLES = {
  High:   { bg: '#FEE2E2', text: '#DC2626', dot: '#DC2626' },
  Medium: { bg: '#FEF3C7', text: '#92400E', dot: '#F59E0B' },
  Low:    { bg: '#DCFCE7', text: '#166534', dot: '#22C55E' },
};

const SCAN_HISTORY_KEY = 'fasalsaathi_scan_history';
const MAX_HISTORY = 20;

/** Load scan history from localStorage */
const loadScanHistory = () => {
  try {
    const raw = localStorage.getItem(SCAN_HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
};

/** Save a new scan entry to localStorage history */
const saveScanToHistory = (scanResult) => {
  if (!scanResult?.results?.length) return;
  const history = loadScanHistory();
  const topPest = scanResult.results[0];
  const entry = {
    id: `scan-${Date.now()}`,
    name: topPest.pest || topPest.class || 'Unknown',
    date: new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    confidence: Math.round((topPest.confidence || 0) * 100),
    severity: topPest.severity?.replace(/[🔴🟡🟢]\s*/g, '').trim() || 'Medium',
    totalDetected: scanResult.total || 1,
    timestamp: Date.now(),
  };
  const updated = [entry, ...history].slice(0, MAX_HISTORY);
  localStorage.setItem(SCAN_HISTORY_KEY, JSON.stringify(updated));
  return updated;
};

const ScanPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedFile, setSelectedFile]   = useState(null);
  const [isScanning,   setIsScanning]     = useState(false);
  const [scanResult,   setScanResult]     = useState(null);   // API response
  const [scanError,    setScanError]      = useState(null);
  const [isDragging,   setIsDragging]     = useState(false);
  const [scanHistory,  setScanHistory]    = useState([]);
  const fileInputRef = useRef(null);

  const navigate = useNavigate();
  const { injectScanContext } = useChatStore();

  // Load scan history on mount
  useEffect(() => { setScanHistory(loadScanHistory()); }, []);

  const handleChatHandoff = () => {
    if (!scanResult) return;
    // Fire off the context injection (runs in background) and navigate immediately
    // so the user sees the chat page with the thinking indicator while AI responds
    injectScanContext(scanResult);
    navigate('/chat');
  };

  const clearHistory = useCallback(() => {
    localStorage.removeItem(SCAN_HISTORY_KEY);
    setScanHistory([]);
  }, []);

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
      const result = await api.detectPest(selectedFile);
      setScanResult(result);
      // Save to persistent scan history
      const updatedHistory = saveScanToHistory(result);
      if (updatedHistory) setScanHistory(updatedHistory);
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
                    padding: '14px', background: isScanning ? 'var(--color-border)' : 'linear-gradient(135deg,#1A7A40,#2D8F55)',
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
            <div style={{ background: '#FEF2F2', borderRadius: '14px', border: '1px solid #FECACA', borderLeft: '4px solid #DC2626', padding: '16px 20px', animation: 'fadeIn 0.3s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <AlertCircle size={20} color="#DC2626" />
                <span style={{ fontWeight: 700, color: '#DC2626' }}>Detection Failed</span>
              </div>
              <p style={{ color: '#7F1D1D', fontSize: '0.875rem', margin: '0 0 12px' }}>{scanError}</p>
              <p style={{ color: '#991B1B', fontSize: '0.8rem', margin: 0 }}>
                💡 Make sure the backend server is running: <code style={{ background: '#FEE2E2', padding: '2px 6px', borderRadius: '6px' }}>cd backend && uvicorn main:app --port 8000</code>
              </p>
            </div>
          )}

          {/* ── No detections ─────────────────────────────────────────── */}
          {scanResult && !hasPests && (
            <div style={{ background: '#F0FDF4', borderRadius: '14px', border: '1px solid #BBF7D0', borderLeft: '4px solid #22C55E', padding: '20px', animation: 'fadeIn 0.4s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <CheckCircle2 size={22} color="#22C55E" />
                <div>
                  <p style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: '#166534', margin: 0 }}>Fasal Swasth Hai! 🌿</p>
                  <p style={{ color: '#16A34A', fontSize: '0.85rem', margin: '4px 0 0' }}>No pests detected in the uploaded image.</p>
                </div>
              </div>
            </div>
          )}

          {/* ── Detection Result ──────────────────────────────────────── */}
          {hasPests && (
            <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid #E5E7EB', borderLeft: '4px solid #1A7A40', padding: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)', animation: 'fadeIn 0.4s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <CheckCircle2 size={22} color="#1A7A40" />
                <span style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: '#1A7A40', fontSize: '0.95rem' }}>
                  {scanResult.total} Pest{scanResult.total > 1 ? 's' : ''} Detected
                </span>
              </div>
              {scanResult.results.map((det, i) => {
                const sevRaw = det.severity || 'Medium';
                const sev = sevRaw.replace(/[🔴🟡🟢]\s*/g, '').trim();
                const style = SEVERITY_STYLES[sev] || SEVERITY_STYLES.Medium;
                return (
                  <div key={i} style={{ marginBottom: i < scanResult.results.length - 1 ? '12px' : 0 }}>
                    <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.25rem', fontWeight: 800, color: '#1A2B1A', margin: '0 0 8px' }}>
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
            <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid #E5E7EB', padding: '24px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
              <h4 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1rem', fontWeight: 700, color: '#1A2B1A', margin: '0 0 16px' }}>
                <AlertCircle size={18} color="#F59E0B" /> Treatment Recommendations
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {scanResult.suggestions.map((tip, i) => (
                  <div key={i} style={{ display: 'flex', gap: '10px', padding: '12px 14px', background: '#F9FAFB', borderRadius: '10px' }}>
                    <span style={{ color: '#1A7A40', fontWeight: 700, flexShrink: 0 }}>✓</span>
                    <span style={{ fontSize: '0.875rem', color: '#1A2B1A', lineHeight: 1.5 }}>{tip}</span>
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '20px' }}>
                <button
                  onClick={handleChatHandoff}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '13px', background: '#fff', color: '#1A7A40', border: '2px solid #1A7A40', borderRadius: '12px', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 4px 12px rgba(26,122,64,0.1)' }}
                  onMouseEnter={e => { e.currentTarget.style.background = '#F0FDF4'; e.currentTarget.style.transform = 'translateY(-1px)'; }}
                  onMouseLeave={e => { e.currentTarget.style.background = '#fff'; e.currentTarget.style.transform = 'none'; }}
                >
                  <MessageCircle size={18} /> Chat with AI Expert about this
                </button>
                <button
                  onClick={clearImage}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '13px', background: 'transparent', color: '#6B7280', border: 'none', borderRadius: '12px', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer', transition: 'all 0.2s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(0,0,0,0.04)'}
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

          {/* Recent Scans — from real YOLO detections */}
          <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 1px 8px rgba(0,0,0,0.05)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: '#1A2B1A', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <History size={17} color="#1A7A40" /> Recent Scans
              </h3>
              {scanHistory.length > 0 && (
                <button
                  onClick={clearHistory}
                  style={{ fontSize: '0.75rem', color: '#8A9A8A', fontWeight: 600, border: 'none', background: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
                  onMouseEnter={e => e.currentTarget.style.color = '#DC2626'}
                  onMouseLeave={e => e.currentTarget.style.color = '#8A9A8A'}
                >
                  <Trash2 size={13} /> Clear
                </button>
              )}
            </div>
            {scanHistory.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px 12px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: '#F3F4F6', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px' }}>
                  <ScanLine size={22} color="#9CA3AF" />
                </div>
                <p style={{ fontWeight: 600, color: '#6B7280', fontSize: '0.875rem', margin: '0 0 4px' }}>No scans yet</p>
                <p style={{ color: '#9CA3AF', fontSize: '0.78rem', margin: 0 }}>Upload a crop photo and scan to start building your history</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {scanHistory.slice(0, 5).map(scan => {
                  const sevColors = { High: '#DC2626', Medium: '#F59E0B', Low: '#22C55E' };
                  const color = sevColors[scan.severity] || '#F59E0B';
                  return (
                    <div key={scan.id} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', borderRadius: '12px', background: '#F9FAFB', transition: 'background 0.15s' }}
                      onMouseEnter={e => e.currentTarget.style.background = '#F0FDF4'}
                      onMouseLeave={e => e.currentTarget.style.background = '#F9FAFB'}>
                      <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: `${color}18`, border: `1.5px solid ${color}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <ScanLine size={16} color={color} />
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <p style={{ fontWeight: 600, color: '#1A2B1A', margin: 0, fontSize: '0.875rem' }}>{scan.name}</p>
                        <p style={{ color: '#6B7280', fontSize: '0.75rem', margin: '1px 0 0' }}>{scan.date}</p>
                      </div>
                      <span style={{ fontSize: '0.7rem', fontWeight: 700, color: color, background: `${color}15`, padding: '3px 8px', borderRadius: '8px', flexShrink: 0 }}>{scan.severity}</span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* How it Works */}
          <div style={{ background: '#fff', borderRadius: '16px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 1px 8px rgba(0,0,0,0.05)' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: '#1A2B1A', margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Info size={16} color="#1A7A40" /> How It Works
            </h3>
            {[
              { n: 1, title: 'Upload Photo', desc: 'Click a clear image of your affected crop' },
              { n: 2, title: 'AI Analyzes', desc: 'YOLOv8 model detects pest type & severity' },
              { n: 3, title: 'Get Treatment', desc: 'Receive detailed treatment recommendations' },
            ].map(step => (
              <div key={step.n} style={{ display: 'flex', gap: '14px', marginBottom: '14px', alignItems: 'flex-start' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', flexShrink: 0 }}>{step.n}</div>
                <div>
                  <p style={{ fontWeight: 700, color: '#1A2B1A', margin: '0 0 2px', fontSize: '0.875rem' }}>{step.title}</p>
                  <p style={{ color: '#5F6B5F', fontSize: '0.78rem', margin: 0 }}>{step.desc}</p>
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
        @keyframes spin    { to { transform: rotate(360deg); } }
        @keyframes fadeIn  { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </PageWrapper>
  );
};

export default ScanPage;
