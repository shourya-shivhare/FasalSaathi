import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Leaf, CloudRain, Sprout, Bot, TrendingUp, ArrowRight, Shield, Star } from 'lucide-react';
import { useUserStore } from '../stores/useUserStore';

const AnimatedCounter = ({ end, duration = 2000, suffix = '' }) => {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = null;
    const step = (ts) => {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      setCount(Math.floor(p * end));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [end, duration]);
  return <span>{count.toLocaleString()}{suffix}</span>;
};

const features = [
  { icon: CloudRain,   title: 'Real-time Weather',     desc: 'Mausam aur khatron ki turant jaankari',    color: '#3B82F6' },
  { icon: Sprout,      title: 'Smart Field Tracking',  desc: 'Mitti ki sehat ka poora record',            color: '#10B981' },
  { icon: Bot,         title: 'AI-Powered Advisory',   desc: 'Fasal ke liye personalized salah',          color: '#8B5CF6' },
  { icon: TrendingUp,  title: 'Live Market Prices',    desc: 'Aapke mandi ke taze bhav',                  color: '#F59E0B' },
];

const Home = () => {
  const navigate = useNavigate();
  const accessToken = useUserStore((s) => s.accessToken);
  const isOnboarded = useUserStore((s) => s.isOnboarded);

  const handleCta = () => {
    if (accessToken && isOnboarded) navigate('/dashboard');
    else if (accessToken && !isOnboarded) navigate('/onboarding');
    else navigate('/signup');
  };

  return (
    <div style={{ position: 'relative', minHeight: '100vh', fontFamily: "'Inter', sans-serif", overflow: 'hidden' }}>

      {/* Background */}
      <div style={{
        position: 'fixed', inset: 0, zIndex: 0,
        background: 'linear-gradient(160deg, #0A2E18 0%, #0F4C2A 40%, #1A5C30 70%, #0D3B20 100%)',
      }} />
      {/* Subtle pattern overlay */}
      <div style={{
        position: 'fixed', inset: 0, zIndex: 1, opacity: 0.06,
        backgroundImage: `radial-gradient(circle at 1px 1px, #4ADE80 1px, transparent 0)`,
        backgroundSize: '40px 40px',
      }} />
      {/* Glow orbs */}
      <div style={{ position: 'fixed', top: '-20%', right: '-10%', width: '600px', height: '600px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(26,122,64,0.35) 0%, transparent 70%)', zIndex: 1, pointerEvents: 'none' }} />
      <div style={{ position: 'fixed', bottom: '-20%', left: '-10%', width: '500px', height: '500px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(250,204,21,0.1) 0%, transparent 70%)', zIndex: 1, pointerEvents: 'none' }} />

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>

        {/* TOP NAV */}
        <header style={{
          position: 'sticky', top: 0, zIndex: 50,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 48px', height: '68px',
          background: 'rgba(10,46,24,0.7)', backdropFilter: 'blur(16px)',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '34px', height: '34px', borderRadius: '10px', background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 16px rgba(26,122,64,0.5)' }}>
              <Leaf size={18} color="#fff" />
            </div>
            <span style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.15rem', fontWeight: 700, color: '#fff', letterSpacing: '-0.01em' }}>FasalSaathi</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button onClick={() => navigate('/login')} style={{ padding: '8px 20px', borderRadius: '20px', border: '1.5px solid rgba(255,255,255,0.25)', background: 'transparent', color: '#fff', fontWeight: 500, fontSize: '0.875rem', cursor: 'pointer', transition: 'all 0.15s' }}
              onMouseEnter={e => e.target.style.borderColor = 'rgba(255,255,255,0.6)'}
              onMouseLeave={e => e.target.style.borderColor = 'rgba(255,255,255,0.25)'}>
              Login
            </button>
            <button onClick={handleCta} style={{ padding: '8px 22px', borderRadius: '20px', border: 'none', background: 'linear-gradient(135deg,#1A7A40,#2D8F55)', color: '#fff', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', boxShadow: '0 0 20px rgba(26,122,64,0.4)', transition: 'transform 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.04)'}
              onMouseLeave={e => e.currentTarget.style.transform = ''}>
              Get Started
            </button>
          </div>
        </header>

        {/* HERO */}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 24px 60px', textAlign: 'center' }}>
          {/* Badge */}
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(212,237,218,0.15)', border: '1px solid rgba(212,237,218,0.3)', borderRadius: '20px', padding: '6px 16px', marginBottom: '28px', backdropFilter: 'blur(8px)' }}>
            <Leaf size={14} color='#4ADE80' />
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#86EFAC', letterSpacing: '0.04em' }}>AI-Powered Agriculture Platform</span>
          </div>

          {/* H1 */}
          <h1 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: 'clamp(2.4rem,5vw,4rem)', fontWeight: 800, color: '#fff', margin: '0 0 20px', lineHeight: 1.15, maxWidth: '800px', letterSpacing: '-0.02em', textShadow: '0 2px 24px rgba(0,0,0,0.3)' }}>
            FasalSaathi,{' '}
            <span style={{ background: 'linear-gradient(90deg,#4ADE80,#FACC15)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Farm Smartly</span>
          </h1>

          {/* Subtitle */}
          <p style={{ fontSize: '1.1rem', color: 'rgba(255,255,255,0.75)', maxWidth: '560px', margin: '0 0 40px', lineHeight: 1.65, fontWeight: 400 }}>
            Apni fasal ka poora khayal — mausam, mandi, aur mitti sab ek jagah. AI se kheti karo, smart results pao.
          </p>

          {/* CTA */}
          <button onClick={handleCta} style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', padding: '16px 36px', borderRadius: '50px', border: 'none', background: 'linear-gradient(135deg,#1A7A40,#2D9450)', color: '#fff', fontSize: '1.05rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 0 40px rgba(26,122,64,0.5)', transition: 'all 0.2s', letterSpacing: '-0.01em' }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 48px rgba(26,122,64,0.7)'; }}
            onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '0 0 40px rgba(26,122,64,0.5)'; }}>
            {accessToken && isOnboarded ? 'Enter App' : accessToken && !isOnboarded ? 'Continue setup' : 'Get Started'}{' '}
            <ArrowRight size={18} />
          </button>

          {/* TRUST STRIP */}
          <div style={{ display: 'flex', gap: '20px', marginTop: '56px', flexWrap: 'wrap', justifyContent: 'center' }}>
            {[
              { value: 10000, suffix: '+', label: 'Farmers', icon: '👨‍🌾' },
              { value: 50000, suffix: '+', label: 'Alerts Sent', icon: '🔔' },
              { value: 8, suffix: '', label: 'States Covered', icon: '🗺️' },
            ].map((stat, i) => (
              <div key={i} style={{ background: 'rgba(255,255,255,0.07)', backdropFilter: 'blur(12px)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '20px', padding: '20px 32px', textAlign: 'center', minWidth: '160px' }}>
                <div style={{ fontSize: '1.5rem', marginBottom: '4px' }}>{stat.icon}</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#FACC15', fontFamily: "'Plus Jakarta Sans',sans-serif" }}>
                  <AnimatedCounter end={stat.value} suffix={stat.suffix} />
                </div>
                <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.65)', fontWeight: 500, marginTop: '2px' }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </main>

        {/* FEATURES */}
        <section style={{ padding: '60px 48px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
            {features.map((f, i) => (
              <div key={i} style={{ background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(16px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '24px', padding: '28px', transition: 'all 0.2s', cursor: 'default' }}
                onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.1)'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.06)'; e.currentTarget.style.transform = ''; }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: `${f.color}22`, border: `1px solid ${f.color}44`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
                  <f.icon size={22} color={f.color} />
                </div>
                <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: '#fff', margin: '0 0 8px' }}>{f.title}</h3>
                <p style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.65)', margin: 0, lineHeight: 1.55 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* TESTIMONIAL */}
        <section style={{ padding: '0 48px 60px', maxWidth: '700px', margin: '0 auto', width: '100%', textAlign: 'center' }}>
          <div style={{ background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(16px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '28px', padding: '40px 48px', position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '4px', marginBottom: '20px' }}>
              {[...Array(5)].map((_, i) => <Star key={i} size={16} color="#FACC15" fill="#FACC15" />)}
            </div>
            <p style={{ fontSize: '1.1rem', color: 'rgba(255,255,255,0.85)', fontStyle: 'italic', lineHeight: 1.7, margin: '0 0 20px' }}>
              "Pehle andaze se kaam karta tha, ab FasalSaathi se seedha pata chalta hai ki kab spray karna hai, kab paani dena hai."
            </p>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg,#1A7A40,#FACC15)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, color: '#fff', fontSize: '1rem' }}>R</div>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.9rem' }}>Ramesh Yadav</div>
                <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.78rem' }}>Unnao, Uttar Pradesh</div>
              </div>
            </div>
          </div>
        </section>

        {/* FOOTER CTA */}
        <footer style={{ textAlign: 'center', padding: '32px 24px 48px', borderTop: '1px solid rgba(255,255,255,0.06)', background: 'rgba(0,0,0,0.2)' }}>
          <button onClick={handleCta} style={{ padding: '14px 40px', borderRadius: '50px', border: 'none', background: 'linear-gradient(135deg,#1A7A40,#2D9450)', color: '#fff', fontSize: '1rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 0 30px rgba(26,122,64,0.4)', transition: 'transform 0.15s' }}
            onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.04)'}
            onMouseLeave={e => e.currentTarget.style.transform = ''}>
            {accessToken && isOnboarded ? 'Go to Dashboard' : accessToken && !isOnboarded ? 'Continue onboarding' : 'Shuru Karo — Bilkul Free Hai'}
          </button>
          <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.8rem', marginTop: '16px' }}>© 2025 FasalSaathi. Powered by AI</p>
        </footer>
      </div>
    </div>
  );
};

export default Home;
