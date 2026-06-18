import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Leaf, Loader2, User, Lock, ArrowRight, Globe } from 'lucide-react';
import { useUserStore } from '../../stores/useUserStore';

export const LoginPage = () => {
  const navigate = useNavigate();
  const login = useUserStore((s) => s.login);

  // States
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('ENGLISH');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim()) {
      setError('Please enter your username.');
      return;
    }
    if (!password) {
      setError('Please enter your password.');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      await login(username.trim(), password);
      
      // Update preferred language after successful login
      const updateProfile = useUserStore.getState().updateFarmerProfile;
      try {
        await updateProfile({ preferred_language: selectedLanguage });
      } catch (err) {
        console.error('Failed to update language preference during login:', err);
      }

      const { isOnboarded } = useUserStore.getState();
      navigate(isOnboarded ? '/dashboard' : '/onboarding');
    } catch (err) {
      setError(err?.message || 'Incorrect username or password.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ position: 'relative', minHeight: '100vh', fontFamily: "'Plus Jakarta Sans', sans-serif", overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {/* Background Gradient */}
      <div style={{
        position: 'fixed', inset: 0, zIndex: 0,
        background: 'linear-gradient(160deg, #072211 0%, #0c3c20 40%, #124d29 70%, #082613 100%)',
      }} />
      {/* Background Dots Grid */}
      <div style={{
        position: 'fixed', inset: 0, zIndex: 1, opacity: 0.05,
        backgroundImage: `radial-gradient(circle at 1px 1px, #4ADE80 1px, transparent 0)`,
        backgroundSize: '30px 30px',
      }} />
      {/* Ambient Glow Orbs */}
      <div style={{ position: 'fixed', top: '-15%', right: '-10%', width: '550px', height: '550px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(74,222,128,0.2) 0%, transparent 70%)', zIndex: 1, pointerEvents: 'none' }} />
      <div style={{ position: 'fixed', bottom: '-20%', left: '-10%', width: '500px', height: '500px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(234,179,8,0.06) 0%, transparent 70%)', zIndex: 1, pointerEvents: 'none' }} />

      {/* Main Box */}
      <div style={{ position: 'relative', zIndex: 10, width: '100%', maxWidth: '440px', padding: '0 20px' }}>
        
        {/* Logo and Header */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '24px' }}>
          <div style={{ 
            width: '56px', 
            height: '56px', 
            borderRadius: '16px', 
            background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            boxShadow: '0 8px 24px rgba(26,122,64,0.4)', 
            marginBottom: '16px' 
          }}>
            <Leaf size={28} color="#fff" style={{ margin: 'auto' }} />
          </div>
          <h2 style={{ fontSize: '1.9rem', fontWeight: 800, color: '#fff', letterSpacing: '-0.02em', margin: 0 }}>FasalSaathi</h2>
          <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.95rem', marginTop: '6px', textAlign: 'center' }}>
            Secure Farmer Authentication
          </p>
        </div>

        {/* Card Body */}
        <div style={{ 
          background: 'rgba(255,255,255,0.05)', 
          backdropFilter: 'blur(20px)', 
          border: '1px solid rgba(255,255,255,0.1)', 
          borderRadius: '24px', 
          padding: '32px 28px', 
          boxShadow: '0 24px 48px rgba(0,0,0,0.3)' 
        }}>
          {error && (
            <div style={{ 
              marginBottom: '20px', 
              padding: '12px 16px', 
              borderRadius: '12px', 
              background: 'rgba(220,38,38,0.15)', 
              border: '1px solid rgba(248,113,113,0.3)', 
              color: '#fecaca', 
              fontSize: '0.85rem',
              lineHeight: '1.4'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div>
              <label style={{ display: 'block', color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>
                Username
              </label>
              <div style={{ position: 'relative' }}>
                <div style={{ position: 'absolute', top: '50%', left: '14px', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', color: '#4ADE80' }}>
                  <User size={18} />
                </div>
                <input 
                  type="text" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter username"
                  required
                  style={{ 
                    width: '100%', 
                    background: 'rgba(0,0,0,0.25)', 
                    border: '1px solid rgba(255,255,255,0.1)', 
                    borderRadius: '14px', 
                    padding: '16px 14px 16px 44px', 
                    color: '#fff', 
                    fontSize: '1rem', 
                    outline: 'none', 
                    transition: 'border-color 0.2s', 
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#4ADE80'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <div style={{ position: 'absolute', top: '50%', left: '14px', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', color: '#4ADE80' }}>
                  <Lock size={18} />
                </div>
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  required
                  style={{ 
                    width: '100%', 
                    background: 'rgba(0,0,0,0.25)', 
                    border: '1px solid rgba(255,255,255,0.1)', 
                    borderRadius: '14px', 
                    padding: '16px 14px 16px 44px', 
                    color: '#fff', 
                    fontSize: '1rem', 
                    outline: 'none', 
                    transition: 'border-color 0.2s', 
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#4ADE80'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>
                Preferred Language
              </label>
              <div style={{ position: 'relative' }}>
                <div style={{ position: 'absolute', top: '50%', left: '14px', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', color: '#4ADE80' }}>
                  <Globe size={18} />
                </div>
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  style={{ 
                    width: '100%', 
                    background: 'rgba(0,0,0,0.25)', 
                    border: '1px solid rgba(255,255,255,0.1)', 
                    borderRadius: '14px', 
                    padding: '16px 14px 16px 44px', 
                    color: '#fff', 
                    fontSize: '1rem', 
                    outline: 'none', 
                    transition: 'border-color 0.2s', 
                    boxSizing: 'border-box',
                    appearance: 'none',
                    cursor: 'pointer'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#4ADE80'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                >
                  <option value="ENGLISH" style={{ color: '#000' }}>English</option>
                  <option value="HINDI" style={{ color: '#000' }}>हिंदी (Hindi)</option>
                </select>
                {/* Custom dropdown arrow */}
                <div style={{ position: 'absolute', top: '50%', right: '16px', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'rgba(255,255,255,0.5)' }}>
                  ▼
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button 
              type="submit" 
              disabled={isLoading}
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                gap: '10px', 
                marginTop: '10px', 
                width: '100%', 
                padding: '16px', 
                borderRadius: '14px', 
                border: 'none', 
                background: 'linear-gradient(135deg,#1A7A40,#2D9450)', 
                color: '#fff', 
                fontSize: '1.05rem', 
                fontWeight: 700, 
                cursor: isLoading ? 'not-allowed' : 'pointer', 
                boxShadow: '0 8px 24px rgba(26,122,64,0.3)', 
                transition: 'all 0.2s', 
                opacity: isLoading ? 0.8 : 1 
              }}
              onMouseEnter={e => { if(!isLoading) { e.currentTarget.style.transform = 'translateY(-2px)'; } }}
              onMouseLeave={e => { if(!isLoading) { e.currentTarget.style.transform = ''; } }}
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Signing In...
                </>
              ) : (
                <>
                  Sign In <ArrowRight size={18} />
                </>
              )}
            </button>

            <div style={{ textAlign: 'center', marginTop: '10px' }}>
              <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.85rem' }}>
                Don't have an account?{' '}
                <Link to="/signup" style={{ color: '#4ADE80', textDecoration: 'none', fontWeight: 600 }}>
                  Sign Up here
                </Link>
              </span>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
