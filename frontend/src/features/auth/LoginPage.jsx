import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Leaf, Mail, Lock, LogIn, ArrowRight } from 'lucide-react';
import { useUserStore } from '../../stores/useUserStore';

export const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API delay, then just bypass and go to dashboard
    setTimeout(() => {
      setIsLoading(false);
      navigate('/dashboard');
    }, 1000);
  };

  return (
    <div style={{ position: 'relative', minHeight: '100vh', fontFamily: "'Inter', sans-serif", overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {/* Background */}
      <div style={{
        position: 'fixed', inset: 0, zIndex: 0,
        background: 'linear-gradient(160deg, #0A2E18 0%, #0F4C2A 40%, #1A5C30 70%, #0D3B20 100%)',
      }} />
      <div style={{
        position: 'fixed', inset: 0, zIndex: 1, opacity: 0.06,
        backgroundImage: `radial-gradient(circle at 1px 1px, #4ADE80 1px, transparent 0)`,
        backgroundSize: '40px 40px',
      }} />
      <div style={{ position: 'fixed', top: '-20%', right: '-10%', width: '600px', height: '600px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(26,122,64,0.35) 0%, transparent 70%)', zIndex: 1, pointerEvents: 'none' }} />
      <div style={{ position: 'fixed', bottom: '-20%', left: '-10%', width: '500px', height: '500px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(250,204,21,0.1) 0%, transparent 70%)', zIndex: 1, pointerEvents: 'none' }} />

      {/* Content Container */}
      <div style={{ position: 'relative', zIndex: 10, width: '100%', maxWidth: '420px', padding: '0 24px' }}>
        
        {/* Header/Logo */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '32px', cursor: 'pointer' }} onClick={() => navigate('/')}>
          <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(26,122,64,0.5)', marginBottom: '16px' }}>
            <Leaf size={24} color="#fff" />
          </div>
          <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.8rem', fontWeight: 800, color: '#fff', letterSpacing: '-0.01em', margin: 0 }}>Welcome Back</h2>
          <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: '0.95rem', marginTop: '8px' }}>Log in to access your farm details</p>
        </div>

        {/* Form Card */}
        <div style={{ background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(20px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '24px', padding: '32px', boxShadow: '0 20px 40px rgba(0,0,0,0.2)' }}>
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* Email Field */}
            <div>
              <label style={{ display: 'block', color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px' }}>Email Address</label>
              <div style={{ position: 'relative' }}>
                <div style={{ position: 'absolute', top: '50%', left: '14px', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', color: 'rgba(255,255,255,0.4)' }}>
                  <Mail size={18} />
                </div>
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  style={{ width: '100%', background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', padding: '14px 14px 14px 40px', color: '#fff', fontSize: '0.95rem', outline: 'none', transition: 'border-color 0.2s', boxSizing: 'border-box' }}
                  onFocus={(e) => e.target.style.borderColor = '#4ADE80'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <label style={{ color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600 }}>Password</label>
                <a href="#" style={{ color: '#4ADE80', fontSize: '0.8rem', textDecoration: 'none', fontWeight: 500 }}>Forgot?</a>
              </div>
              <div style={{ position: 'relative' }}>
                <div style={{ position: 'absolute', top: '50%', left: '14px', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', color: 'rgba(255,255,255,0.4)' }}>
                  <Lock size={18} />
                </div>
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  style={{ width: '100%', background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', padding: '14px 14px 14px 40px', color: '#fff', fontSize: '0.95rem', outline: 'none', transition: 'border-color 0.2s', boxSizing: 'border-box' }}
                  onFocus={(e) => e.target.style.borderColor = '#4ADE80'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                />
              </div>
            </div>

            {/* Submit Button */}
            <button 
              type="submit" 
              disabled={isLoading}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginTop: '10px', width: '100%', padding: '16px', borderRadius: '14px', border: 'none', background: 'linear-gradient(135deg,#1A7A40,#2D9450)', color: '#fff', fontSize: '1.05rem', fontWeight: 700, cursor: isLoading ? 'not-allowed' : 'pointer', boxShadow: '0 0 20px rgba(26,122,64,0.4)', transition: 'all 0.2s', opacity: isLoading ? 0.8 : 1 }}
              onMouseEnter={e => { if(!isLoading) { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 30px rgba(26,122,64,0.6)'; } }}
              onMouseLeave={e => { if(!isLoading) { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '0 0 20px rgba(26,122,64,0.4)'; } }}
            >
              {isLoading ? 'Logging in...' : (
                <>
                  Log In <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>
          
          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', margin: '24px 0', gap: '12px' }}>
            <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.1)' }}></div>
            <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.8rem', fontWeight: 500 }}>OR</span>
            <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.1)' }}></div>
          </div>
          
          {/* Register Link */}
          <div style={{ textAlign: 'center', color: 'rgba(255,255,255,0.65)', fontSize: '0.9rem' }}>
            New to FasalSaathi?{' '}
            <Link to="/signup" style={{ color: '#4ADE80', fontWeight: 600, textDecoration: 'none' }}>Create Account</Link>
          </div>
        </div>
      </div>
    </div>
  );
};
