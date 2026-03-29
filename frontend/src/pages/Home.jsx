import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sun, Moon, CloudRain, Sprout, Bot, TrendingUp, ArrowRight } from 'lucide-react';
import { useThemeStore } from '../stores/useThemeStore';
import { useUserStore } from '../stores/useUserStore';

const AnimatedCounter = ({ end, duration = 2000, suffix = '' }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      setCount(Math.floor(progress * end));
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    window.requestAnimationFrame(step);
  }, [end, duration]);

  return <span>{count.toLocaleString()}{suffix}</span>;
};

const Home = () => {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useThemeStore();
  const { isOnboarded } = useUserStore();
  const isDark = theme === 'dark';

  const handleCtaClick = () => {
    if (isOnboarded) {
      navigate('/dashboard');
    } else {
      navigate('/onboarding');
    }
  };

  const features = [
    {
      icon: CloudRain,
      title: "Real-time Weather & Alerts",
      description: "Mausam aur khatron ki turant jaankari",
      color: "text-blue-500"
    },
    {
      icon: Sprout,
      title: "Smart Soil & Field Tracking",
      description: "Mitti ki sehat ka poora record",
      color: "text-green-500"
    },
    {
      icon: Bot,
      title: "AI-Powered Advisory",
      description: "Fasal ke liye smart salah",
      color: "text-purple-500"
    },
    {
      icon: TrendingUp,
      title: "Local Market Prices",
      description: "Aapke mandi ke taze bhav",
      color: "text-orange-500"
    }
  ];

  return (
    <div className="relative min-h-screen font-sans">
      {/* Background Image & Overlay */}
      <div 
        className="fixed inset-0 z-0 bg-cover bg-center"
        style={{ backgroundImage: "url('https://images.unsplash.com/photo-1592982537447-69c3a3ef89c3?auto=format&fit=crop&q=80')" }}
      />
      <div className="fixed inset-0 hero-overlay" />

      {/* Main Content Area */}
      <div className="relative z-20 flex flex-col min-h-screen">
        
        {/* Sticky Header */}
        <header className="sticky top-0 w-full px-4 md:px-8 py-4 flex items-center justify-between backdrop-blur-md bg-white/10 dark:bg-black/20 border-b border-white/10 z-50">
          <div className="flex items-center gap-2">
            <span className="text-2xl pt-1">🌱</span>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white drop-shadow-md">
              FasalSaathi
            </h1>
          </div>
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full backdrop-blur-md bg-white/20 dark:bg-black/40 border border-white/20 transition-all hover:bg-white/30 text-white"
            title="Toggle theme"
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </header>

        {/* Hero Section */}
        <main className="flex-1 flex flex-col items-center justify-center px-4 py-16 text-center text-white">
          <h2 className="text-4xl md:text-6xl font-extrabold mb-4 drop-shadow-lg leading-tight">
            FasalSaathi, <br className="md:hidden"/> Farm smartly
          </h2>
          <p className="text-lg md:text-xl max-w-2xl mx-auto mb-8 text-white/90 drop-shadow-md font-medium">
            Apni fasal ka poora khayal — mausam, mandi, aur mitti sab ek jagah.
          </p>
          <button 
            onClick={handleCtaClick}
            className="flex items-center gap-2 px-8 py-4 rounded-full bg-green-600 hover:bg-green-500 text-white font-bold text-lg transition-transform transform hover:scale-105 shadow-[0_0_20px_rgba(22,163,74,0.4)] border border-green-400/30"
          >
            {isOnboarded ? 'Enter App' : 'Get Started'} <ArrowRight className="w-5 h-5 pt-0.5" />
          </button>

          {/* Trust Strip */}
          <div className="mt-16 grid grid-cols-3 gap-4 md:gap-8 w-full max-w-4xl mx-auto px-2">
            <div className="flex flex-col items-center p-3 md:p-4 backdrop-blur-md bg-white/10 dark:bg-black/30 border border-white/20 rounded-2xl">
              <span className="text-xl md:text-3xl font-bold text-green-300 drop-shadow"><AnimatedCounter end={10000} suffix="+" /></span>
              <span className="text-xs md:text-sm text-white/80 mt-1 font-medium">Farmers</span>
            </div>
            <div className="flex flex-col items-center p-3 md:p-4 backdrop-blur-md bg-white/10 dark:bg-black/30 border border-white/20 rounded-2xl">
              <span className="text-xl md:text-3xl font-bold text-green-300 drop-shadow"><AnimatedCounter end={50000} suffix="+" /></span>
              <span className="text-xs md:text-sm text-white/80 mt-1 font-medium">Alerts Sent</span>
            </div>
            <div className="flex flex-col items-center p-3 md:p-4 backdrop-blur-md bg-white/10 dark:bg-black/30 border border-white/20 rounded-2xl">
              <span className="text-xl md:text-3xl font-bold text-green-300 drop-shadow"><AnimatedCounter end={8} /></span>
              <span className="text-xs md:text-sm text-white/80 mt-1 font-medium">States Covered</span>
            </div>
          </div>
        </main>

        {/* Features Section */}
        <section className="px-4 py-16 w-full max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, idx) => (
              <div 
                key={idx}
                className="backdrop-blur-xl bg-white/20 dark:bg-black/40 border border-white/20 rounded-3xl p-6 transition-all hover:bg-white/30 dark:hover:bg-black/50"
              >
                <div className={`w-12 h-12 rounded-2xl mb-4 flex items-center justify-center backdrop-blur-md bg-white/40 dark:bg-black/50 border border-white/20 ${feature.color}`}>
                  <feature.icon className="w-6 h-6 drop-shadow-md" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2 drop-shadow-md">{feature.title}</h3>
                <p className="text-white/80 text-sm font-medium">{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Testimonial Strip */}
        <section className="px-4 pb-16 w-full max-w-3xl mx-auto text-center">
          <div className="backdrop-blur-xl bg-white/10 dark:bg-black/30 border border-white/20 rounded-3xl p-8 relative">
            <span className="absolute top-4 left-6 text-6xl text-white/20 font-serif leading-none">"</span>
            <p className="text-lg md:text-xl text-white/90 italic font-medium mb-4 z-10 relative">
              Pehle andaze se kaam karta tha, ab FasalSaathi se seedha pata chalta hai.
            </p>
            <p className="text-sm text-white/70 font-bold">— Ramesh Yadav, Unnao, UP</p>
          </div>
        </section>

        {/* Footer CTA */}
        <footer className="w-full flex flex-col items-center justify-center pb-20 pt-8 mt-auto backdrop-blur-md bg-gradient-to-t from-black/80 to-transparent">
          <button 
            onClick={handleCtaClick}
            className="px-8 py-4 rounded-full bg-green-600 hover:bg-green-500 text-white font-bold text-lg transition-transform transform hover:scale-105 shadow-lg border border-green-400/30"
          >
            {isOnboarded ? 'Enter App' : 'Get Started'}
          </button>
          <p className="text-white/80 mt-3 font-medium text-sm">Shuru karo, bilkul free hai.</p>
        </footer>

      </div>
    </div>
  );
};

export default Home;
