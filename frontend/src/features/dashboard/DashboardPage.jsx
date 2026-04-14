import React from 'react';
import { Camera, ScanLine, TrendingUp, Leaf, Bell, CloudSun, ShieldAlert } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { WeatherCard } from './components/WeatherCard';
import { SoilHealthGrid } from './components/SoilHealthGrid';
import { CropStatusBanner } from './components/CropStatusBanner';
import { IrrigationTimer } from './components/IrrigationTimer';
import { AlertsFeed } from './components/AlertsFeed';
import { useFieldData } from './hooks/useFieldData';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { mockAlerts } from '../../lib/mockData.jsx';

const StatCard = ({ icon: Icon, label, value, sub }) => (
  <div style={{
    background: 'var(--color-surface)',
    borderRadius: '16px',
    padding: '20px 24px',
    boxShadow: '0 1px 8px rgba(26,122,64,0.07)',
    border: '1px solid var(--color-border)',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    flex: '1',
    minWidth: '0',
  }}>
    <div style={{
      width: '48px', height: '48px', borderRadius: '12px',
      background: 'var(--color-section-header-bg)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexShrink: 0,
    }}>
      <Icon size={22} color="var(--color-accent-primary)" />
    </div>
    <div>
      <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--color-text-primary)', lineHeight: 1.1 }}>{value}</div>
      <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginTop: '2px' }}>{label}</div>
      {sub && <div style={{ fontSize: '0.72rem', color: 'var(--color-accent-primary)', fontWeight: 600, marginTop: '2px' }}>{sub}</div>}
    </div>
  </div>
);

const DashboardPage = () => {
  const navigate = useNavigate();
  const { farmer, logout } = useUserStore();
  const { activeField, weather, soil, irrigation, hasFields, isLoading } = useFieldData();

  if (isLoading) {
    return (
      <PageWrapper>
        <div className="space-y-4 animate-pulse">
          <div style={{ height: '80px', background: 'var(--color-surface-hover)', borderRadius: '16px' }} />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '16px' }}>
            {[1, 2, 3, 4].map(i => (
              <div key={i} style={{ height: '96px', background: 'var(--color-surface-hover)', borderRadius: '16px' }} />
            ))}
          </div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px' }}>
        <div>
          <h1 style={{
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            fontSize: '1.65rem', fontWeight: 700,
            color: 'var(--color-text-primary)', margin: 0,
          }}>
            Good morning, {farmer?.name?.split(' ')[0] || 'Farmer'} 🌱
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            {hasFields ? `Managing ${activeField?.name || 'your farm'} · ${farmer?.village || 'India'}` : 'Welcome to FasalSaathi'}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            background: 'var(--color-surface)', borderRadius: '12px', padding: '8px 16px',
            border: '1px solid var(--color-border)',
            boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
            fontSize: '0.85rem', color: 'var(--color-text-secondary)',
          }}>
            <CloudSun size={18} color="#92400E" />
            <span>28°C · Sunny</span>
          </div>
          <button style={{
            width: '40px', height: '40px', borderRadius: '12px',
            background: 'var(--color-surface)', border: '1px solid var(--color-border)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
          }}>
            <Bell size={18} color="var(--color-text-secondary)" />
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <StatCard icon={Leaf} label="Crops Monitored" value={hasFields ? '12' : '0'} />
        <StatCard icon={ShieldAlert} label="Pests Detected" value="3" sub="This month" />
        <StatCard icon={ScanLine} label="Scans This Week" value="8" />
        <StatCard icon={TrendingUp} label="Market Index" value="+2.4%" sub="↑ Wheat up today" />
      </div>

      {/* Scan & Schemes CTAs */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        <div
          onClick={() => navigate('/detect')}
          style={{
            background: 'linear-gradient(135deg, #1A7A40, #2D8F55)',
            borderRadius: '16px',
            padding: '20px 28px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(26,122,64,0.25)',
            transition: 'transform 0.15s, box-shadow 0.15s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 8px 28px rgba(26,122,64,0.35)';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.transform = '';
            e.currentTarget.style.boxShadow = '0 4px 20px rgba(26,122,64,0.25)';
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '48px', height: '48px', borderRadius: '12px',
              background: 'rgba(255,255,255,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Camera size={24} color="#fff" />
            </div>
            <div>
              <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: '#fff' }}>
                Scan Your Crop
              </div>
              <div style={{ fontSize: '0.83rem', color: 'rgba(255,255,255,0.8)', marginTop: '2px' }}>
                Instant pest detection
              </div>
            </div>
          </div>
        </div>

        <div
          onClick={() => navigate('/schemes')}
          style={{
            background: 'linear-gradient(135deg, #0f766e, #14b8a6)',
            borderRadius: '16px',
            padding: '20px 28px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(15,118,110,0.25)',
            transition: 'transform 0.15s, box-shadow 0.15s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 8px 28px rgba(15,118,110,0.35)';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.transform = '';
            e.currentTarget.style.boxShadow = '0 4px 20px rgba(15,118,110,0.25)';
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '48px', height: '48px', borderRadius: '12px',
              background: 'rgba(255,255,255,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Leaf size={24} color="#fff" />
            </div>
            <div>
              <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1rem', fontWeight: 700, color: '#fff' }}>
                Gov Schemes
              </div>
              <div style={{ fontSize: '0.83rem', color: 'rgba(255,255,255,0.8)', marginTop: '2px' }}>
                Find eligible schemes
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Two-column: Weather + Irrigation */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        <WeatherCard weather={weather} />
        <IrrigationTimer irrigation={irrigation} />
      </div>

      {/* Soil Health */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{
          fontFamily: "'Plus Jakarta Sans',sans-serif",
          fontSize: '1.05rem', fontWeight: 700,
          color: 'var(--color-text-primary)', marginBottom: '12px', marginTop: 0,
        }}>
          🌱 Soil Health
        </h2>
        <SoilHealthGrid soil={soil} />
      </div>

      {/* Crop Status */}
      {hasFields && activeField && <CropStatusBanner field={activeField} />}

      {/* Alerts Feed */}
      <AlertsFeed alerts={mockAlerts} />

      {/* Empty State */}
      {!hasFields && (
        <div style={{
          textAlign: 'center', padding: '48px', borderRadius: '16px',
          border: '2px dashed var(--color-border)', background: 'var(--color-surface)', marginTop: '16px',
        }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>🌱</div>
          <h3 style={{ fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: '8px' }}>No fields added yet</h3>
          <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>Add your first field to start tracking your farm</p>
        </div>
      )}

      {/* Dev Reset */}
      {import.meta.env.DEV && (
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '40px', paddingBottom: '16px' }}>
          <button
            onClick={() => { logout(); window.location.href = '/'; }}
            style={{
              padding: '6px 16px', background: 'rgba(220,38,38,0.8)',
              color: '#fff', borderRadius: '8px', border: 'none',
              cursor: 'pointer', fontSize: '0.8rem', opacity: 0.6,
            }}
          >
            Reset Testing State (Dev Only)
          </button>
        </div>
      )}
    </PageWrapper>
  );
};

export { DashboardPage };