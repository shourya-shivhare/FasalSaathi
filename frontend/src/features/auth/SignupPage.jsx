import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Leaf, Phone, Key, ArrowRight, ArrowLeft, Loader2, User, Lock } from 'lucide-react';
import { useUserStore } from '../../stores/useUserStore';

export const SignupPage = () => {
  const navigate = useNavigate();
  const signupSendOtp = useUserStore((s) => s.signupSendOtp);
  const signupVerify = useUserStore((s) => s.signupVerify);

  // States
  const [username, setUsername] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [channel, setChannel] = useState('SMS'); // SMS or WHATSAPP
  const [step, setStep] = useState(1); // 1: Registration fields, 2: OTP Entry
  const [otp, setOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Timer for resend
  const [timer, setTimer] = useState(0);

  useEffect(() => {
    let interval;
    if (timer > 0) {
      interval = setInterval(() => {
        setTimer((t) => t - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [timer]);

  const handlePhoneChange = (e) => {
    const val = e.target.value.replace(/\D/g, ''); // keep only digits
    setPhoneNumber(val);
  };

  const formattedPhoneNumber = () => {
    let num = phoneNumber.trim();
    if (!num.startsWith('+')) {
      if (num.startsWith('91') && num.length > 10) {
        num = '+' + num;
      } else {
        num = '+91' + num;
      }
    }
    return num;
  };

  const handleSignupSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!username.trim()) {
      setError('Please choose a username.');
      return;
    }
    if (phoneNumber.length < 10) {
      setError('Please enter a valid 10-digit phone number.');
      return;
    }
    if (!password) {
      setError('Please enter a password.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setError(null);
    setIsLoading(true);
    const fullPhone = formattedPhoneNumber();

    try {
      await signupSendOtp(username.trim(), fullPhone, password, channel);
      setStep(2);
      setTimer(60); // 60s cooldown
    } catch (err) {
      setError(err?.message || 'Username or Phone number is already registered.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if (otp.length < 4) {
      setError('Please enter a valid OTP code.');
      return;
    }

    setError(null);
    setIsLoading(true);
    const fullPhone = formattedPhoneNumber();

    try {
      await signupVerify(username.trim(), fullPhone, password, otp, 'Web Browser', false);
      navigate('/onboarding');
    } catch (err) {
      setError(err?.message || 'Incorrect OTP code. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToFields = () => {
    setStep(1);
    setOtp('');
    setError(null);
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
      <div style={{ position: 'relative', zIndex: 10, width: '100%', maxWidth: '440px', padding: '24px 20px' }}>
        
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
            Create Farmer Account &amp; Verify Phone
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

          {step === 1 ? (
            /* Step 1: Username, Phone, Password, Confirm Password */
            <form onSubmit={handleSignupSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Choose Username
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
                      padding: '14px 14px 14px 44px', 
                      color: '#fff', 
                      fontSize: '0.95rem', 
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
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Mobile Number
                </label>
                <div style={{ position: 'relative' }}>
                  <div style={{ 
                    position: 'absolute', 
                    top: '50%', 
                    left: '14px', 
                    transform: 'translateY(-50%)', 
                    color: '#4ADE80',
                    fontSize: '0.95rem',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <Phone size={18} />
                    <span>+91</span>
                  </div>
                  <input 
                    type="tel" 
                    value={phoneNumber.startsWith('91') && phoneNumber.length > 10 ? phoneNumber.substring(2) : phoneNumber}
                    onChange={handlePhoneChange}
                    placeholder="Enter 10-digit number"
                    maxLength={10}
                    required
                    style={{ 
                      width: '100%', 
                      background: 'rgba(0,0,0,0.25)', 
                      border: '1px solid rgba(255,255,255,0.1)', 
                      borderRadius: '14px', 
                      padding: '14px 14px 14px 72px', 
                      color: '#fff', 
                      fontSize: '0.95rem', 
                      outline: 'none', 
                      transition: 'border-color 0.2s', 
                      boxSizing: 'border-box',
                      letterSpacing: '0.05em'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#4ADE80'}
                    onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
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
                      padding: '14px 14px 14px 44px', 
                      color: '#fff', 
                      fontSize: '0.95rem', 
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
                <label style={{ display: 'block', color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Confirm Password
                </label>
                <div style={{ position: 'relative' }}>
                  <div style={{ position: 'absolute', top: '50%', left: '14px', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', color: '#4ADE80' }}>
                    <Lock size={18} />
                  </div>
                  <input 
                    type="password" 
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm password"
                    required
                    style={{ 
                      width: '100%', 
                      background: 'rgba(0,0,0,0.25)', 
                      border: '1px solid rgba(255,255,255,0.1)', 
                      borderRadius: '14px', 
                      padding: '14px 14px 14px 44px', 
                      color: '#fff', 
                      fontSize: '0.95rem', 
                      outline: 'none', 
                      transition: 'border-color 0.2s', 
                      boxSizing: 'border-box'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#4ADE80'}
                    onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                  />
                </div>
              </div>

              {/* Submit Registration Button */}
              <button 
                type="submit" 
                disabled={isLoading}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justify: 'center', 
                  gap: '10px', 
                  marginTop: '12px', 
                  width: '100%', 
                  padding: '14px', 
                  borderRadius: '14px', 
                  border: 'none', 
                  background: 'linear-gradient(135deg,#1A7A40,#2D9450)', 
                  color: '#fff', 
                  fontSize: '1rem', 
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
                    <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Sending OTP...
                  </>
                ) : (
                  <>
                    Sign Up &amp; Send OTP <ArrowRight size={18} />
                  </>
                )}
              </button>

              <div style={{ textAlign: 'center', marginTop: '10px' }}>
                <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.85rem' }}>
                  Already have an account?{' '}
                  <Link to="/login" style={{ color: '#4ADE80', textDecoration: 'none', fontWeight: 600 }}>
                    Sign In here
                  </Link>
                </span>
              </div>
            </form>
          ) : (
            /* Step 2: OTP Verification */
            <form onSubmit={handleVerifyOtp} style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <label style={{ color: 'rgba(255,255,255,0.85)', fontSize: '0.85rem', fontWeight: 600 }}>
                    Enter OTP Code
                  </label>
                  <button 
                    type="button" 
                    onClick={handleBackToFields} 
                    style={{ 
                      background: 'none', 
                      border: 'none', 
                      color: '#4ADE80', 
                      fontSize: '0.8rem', 
                      cursor: 'pointer', 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '4px',
                      fontWeight: 600
                    }}
                  >
                    <ArrowLeft size={12} /> Go Back
                  </button>
                </div>
                
                <p style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.5)', marginTop: '-4px', marginBottom: '14px' }}>
                  Sent to +91 {phoneNumber}
                </p>

                <div style={{ position: 'relative' }}>
                  <div style={{ position: 'absolute', top: '50%', left: '14px', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', color: 'rgba(255,255,255,0.4)' }}>
                    <Key size={18} />
                  </div>
                  <input 
                    type="text" 
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                    placeholder="Enter code"
                    maxLength={6}
                    required
                    style={{ 
                      width: '100%', 
                      background: 'rgba(0,0,0,0.25)', 
                      border: '1px solid rgba(255,255,255,0.1)', 
                      borderRadius: '14px', 
                      padding: '16px 14px 16px 44px', 
                      color: '#fff', 
                      fontSize: '1.15rem', 
                      outline: 'none', 
                      transition: 'border-color 0.2s', 
                      boxSizing: 'border-box',
                      letterSpacing: '0.25em',
                      textAlign: 'center'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#4ADE80'}
                    onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                  />
                </div>
              </div>

              {/* Submit OTP Button */}
              <button 
                type="submit" 
                disabled={isLoading}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justify: 'center', 
                  gap: '10px', 
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
                    <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Verifying Code...
                  </>
                ) : (
                  <>
                    Verify OTP &amp; Complete Signup <ArrowRight size={18} />
                  </>
                )}
              </button>

              {/* Resend Option */}
              <div style={{ textAlign: 'center', marginTop: '6px' }}>
                {timer > 0 ? (
                  <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.85rem' }}>
                    Resend code in {timer}s
                  </span>
                ) : (
                  <button
                    type="button"
                    onClick={handleSignupSubmit}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#4ADE80',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      textDecoration: 'underline'
                    }}
                  >
                    Resend OTP code
                  </button>
                )}
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
