import React, { useMemo, useEffect } from 'react';
import { Camera, ScanLine, TrendingUp, Leaf, Bell, CloudSun, ShieldAlert, Sun, Cloud, CloudRain, Zap, MapPin, Sprout } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { WeatherCard } from './components/WeatherCard';
import { SoilHealthGrid } from './components/SoilHealthGrid';
import { CropStatusBanner } from './components/CropStatusBanner';
import { IrrigationTimer } from './components/IrrigationTimer';
import { AlertsFeed } from './components/AlertsFeed';
import { useFieldData } from './hooks/useFieldData';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { useFarmStore } from '../../stores/useFarmStore.jsx';
import { useCropCycleStore } from '../../stores/useCropCycleStore.jsx';
import { useNotificationStore } from '../../stores/useNotificationStore.jsx';

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

/** Return a greeting based on the current hour */
const getGreeting = () => {
  const hr = new Date().getHours();
  if (hr < 12) return 'Good morning';
  if (hr < 17) return 'Good afternoon';
  return 'Good evening';
};

/** Get a weather icon for the header chip */
const getWeatherChipIcon = (condition) => {
  if (!condition) return CloudSun;
  const c = condition.toLowerCase();
  if (c.includes('sun') || c.includes('clear')) return Sun;
  if (c.includes('rain') || c.includes('drizzle') || c.includes('shower')) return CloudRain;
  if (c.includes('thunder')) return Zap;
  return Cloud;
};

const DashboardPage = () => {
  const navigate = useNavigate();
  const { farmer, logout } = useUserStore();
  const { activeField, weather, soil, irrigation, hasFields, isLoading, fields, scanHistory } = useFieldData();
  const { farms, fetchFarms } = useFarmStore();
  const { cycles, fetchCycles } = useCropCycleStore();
  const { notifications } = useNotificationStore();

  useEffect(() => { fetchFarms(); fetchCycles(); }, []);

  // Derive real stats from actual data
  const stats = useMemo(() => {
    const totalCrops = [...new Set(fields.map(f => f.crop).filter(Boolean))].length;
    const totalScans = (scanHistory || []).length;
    const recentPests = (scanHistory || []).filter(s => {
      const d = new Date(s.timestamp);
      const now = new Date();
      return (now - d) < 30 * 24 * 60 * 60 * 1000; // last 30 days
    }).length;

    return { totalCrops, totalScans, recentPests };
  }, [fields, scanHistory]);

  // Generate contextual alerts from real data
  const alerts = useMemo(() => {
    const result = [];

    // Weather-based alert
    if (weather?.riskLevel === 'HIGH') {
      result.push({
        id: 'alert-weather',
        type: 'weather_warning',
        title: `${weather.condition} — High Risk`,
        message: `Temperature is ${weather.temp}°C with ${weather.humidity}% humidity. Take precautions for your crops.`,
        severity: 'high',
        timestamp: new Date(),
        icon: 'Thermometer',
      });
    }

    // Soil-based alert
    if (soil && soil.N < 250) {
      result.push({
        id: 'alert-nitrogen',
        type: 'nutrient_deficiency',
        title: 'Low Nitrogen',
        message: `Nitrogen level is ${soil.N} kg/ha which is below optimal (280+ kg/ha). Consider urea application.`,
        severity: 'medium',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        icon: 'AlertTriangle',
      });
    }
    if (soil && soil.pH && (soil.pH < 5.5 || soil.pH > 8.0)) {
      result.push({
        id: 'alert-ph',
        type: 'nutrient_deficiency',
        title: `Soil pH ${soil.pH < 5.5 ? 'Too Low' : 'Too High'}`,
        message: `pH level is ${soil.pH}. Optimal range is 6.0–7.5 for most crops.`,
        severity: 'medium',
        timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000),
        icon: 'AlertTriangle',
      });
    }

    // Pest detection alert from recent scans
    if (scanHistory?.length > 0) {
      const latest = scanHistory[0];
      result.push({
        id: `alert-pest-${latest.id}`,
        type: 'pest_detection',
        title: `Recent Pest: ${latest.pestName || 'Detected'}`,
        message: latest.message || `Pest detected with ${latest.confidence || 'high'} confidence. Check treatment recommendations.`,
        severity: latest.severity?.toLowerCase() || 'low',
        timestamp: new Date(latest.timestamp),
        icon: 'Bug',
      });
    }

    // If no alerts at all, show a positive one
    if (result.length === 0) {
      result.push({
        id: 'alert-ok',
        type: 'info',
        title: 'All Clear ✓',
        message: 'No alerts at the moment. Your farm is looking good!',
        severity: 'low',
        timestamp: new Date(),
        icon: 'Calendar',
      });
    }

    return result;
  }, [weather, soil, scanHistory]);

  const WeatherChipIcon = getWeatherChipIcon(weather?.condition);

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
            {getGreeting()}, {farmer?.name?.split(' ')[0] || 'Farmer'} 🌱
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: '4px 0 0' }}>
            {hasFields
              ? `Managing ${activeField?.name || 'your farm'} · ${farmer?.district || farmer?.state || 'India'}`
              : 'Welcome to FasalSaathi — add a field to get started'}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {weather && weather.temp !== '--' && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              background: 'var(--color-surface)', borderRadius: '12px', padding: '8px 16px',
              border: '1px solid var(--color-border)',
              boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
              fontSize: '0.85rem', color: 'var(--color-text-secondary)',
            }}>
              <WeatherChipIcon size={18} color="#92400E" />
              <span>{weather.temp}°C · {weather.condition}</span>
            </div>
          )}
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

      {/* Stats Row — all derived from real data */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <StatCard
          icon={Leaf}
          label="Crops Monitored"
          value={stats.totalCrops}
          sub={hasFields ? `${fields.length} field${fields.length > 1 ? 's' : ''}` : null}
        />
        <StatCard
          icon={ShieldAlert}
          label="Pests Detected"
          value={stats.recentPests}
          sub={stats.recentPests > 0 ? 'Last 30 days' : null}
        />
        <StatCard
          icon={ScanLine}
          label="Total Scans"
          value={stats.totalScans}
        />
        <StatCard
          icon={TrendingUp}
          label="Total Land"
          value={`${fields.reduce((s, f) => s + (parseFloat(f.area) || 0), 0).toFixed(1)}`}
          sub="Acres"
        />
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

      {/* ── Farm-Aware Widgets ─────────────────────────────────── */}

      {/* Farm Summary Card */}
      {farms.length > 0 && (
        <div style={{
          background: 'var(--color-surface)', borderRadius: '16px',
          border: '1px solid var(--color-border)', padding: '20px 24px',
          marginBottom: '24px', boxShadow: '0 1px 8px rgba(26,122,64,0.07)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h2 style={{
              fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '1.05rem',
              fontWeight: 700, color: 'var(--color-text-primary)', margin: 0,
            }}>
              🏡 Farm Summary
            </h2>
            <button
              onClick={() => navigate('/farms')}
              style={{
                border: 'none', background: 'none', color: 'var(--color-accent-primary)',
                fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer',
              }}
            >
              Manage farms →
            </button>
          </div>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {farms.slice(0, 4).map((farm) => {
              const fCycles = cycles.filter((c) => c.farm_id === farm.id && c.status === 'ACTIVE');
              return (
                <div key={farm.id} style={{
                  flex: '1 1 200px', background: 'var(--color-bg-primary)', borderRadius: '12px',
                  padding: '14px 18px', border: '1px solid var(--color-border)',
                }}>
                  <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--color-text-primary)', marginBottom: '6px' }}>
                    {farm.farm_name}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--color-text-secondary)', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                    {farm.village && <span><MapPin size={12} style={{verticalAlign: 'middle'}} /> {farm.village}</span>}
                    {farm.total_area && <span>📐 {farm.total_area}ac</span>}
                    <span style={{
                      padding: '1px 8px', borderRadius: '10px', fontSize: '0.7rem', fontWeight: 600,
                      background: '#dcfce7', color: '#16a34a',
                    }}>
                      {fCycles.length} active
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Active Crops Widget */}
      {cycles.filter((c) => c.status === 'ACTIVE').length > 0 && (
        <div style={{
          background: 'var(--color-surface)', borderRadius: '16px',
          border: '1px solid var(--color-border)', padding: '20px 24px',
          marginBottom: '24px', boxShadow: '0 1px 8px rgba(26,122,64,0.07)',
        }}>
          <h2 style={{
            fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '1.05rem',
            fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 14px',
          }}>
            🌱 Active Crops
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '12px' }}>
            {cycles.filter((c) => c.status === 'ACTIVE').slice(0, 6).map((cycle) => {
              const farm = farms.find((f) => f.id === cycle.farm_id);
              const stageColors = {
                SEEDING: '#10b981', GERMINATION: '#34d399', VEGETATIVE: '#22c55e',
                FLOWERING: '#f59e0b', FRUITING: '#f97316', MATURITY: '#ef4444',
              };
              return (
                <div key={cycle.id} style={{
                  background: 'var(--color-bg-primary)', borderRadius: '12px',
                  padding: '14px 18px', border: '1px solid var(--color-border)',
                  borderLeft: `4px solid ${stageColors[cycle.current_stage] || '#6b7280'}`,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <div>
                      <strong style={{ fontSize: '0.92rem', color: 'var(--color-text-primary)' }}>{cycle.crop_name}</strong>
                      {cycle.crop_variety && (
                        <span style={{
                          marginLeft: '8px', fontSize: '0.7rem', fontWeight: 600,
                          padding: '1px 7px', borderRadius: '6px', background: '#ede9fe', color: '#7c3aed',
                        }}>
                          {cycle.crop_variety}
                        </span>
                      )}
                    </div>
                    <span style={{
                      fontSize: '0.68rem', fontWeight: 700, padding: '2px 8px',
                      borderRadius: '20px', background: '#fef3c7', color: '#92400e',
                    }}>
                      {cycle.season}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--color-text-secondary)', display: 'flex', gap: '10px' }}>
                    <span style={{ fontWeight: 600, color: stageColors[cycle.current_stage] || '#6b7280' }}>
                      {cycle.current_stage}
                    </span>
                    {farm && <span>· {farm.farm_name}</span>}
                    {cycle.updated_at && (
                      <span>· {new Date(cycle.updated_at).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Market & Pest Alerts from Notifications */}
      {notifications.filter((n) => !n.is_read).length > 0 && (
        <div style={{
          background: 'var(--color-surface)', borderRadius: '16px',
          border: '1px solid var(--color-border)', padding: '20px 24px',
          marginBottom: '24px', boxShadow: '0 1px 8px rgba(26,122,64,0.07)',
        }}>
          <h2 style={{
            fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '1.05rem',
            fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 14px',
          }}>
            ⚡ Recent Alerts
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {notifications.filter((n) => !n.is_read).slice(0, 5).map((n) => (
              <div key={n.id} style={{
                display: 'flex', alignItems: 'center', gap: '12px',
                padding: '10px 14px', borderRadius: '10px',
                background: 'var(--color-bg-primary)', border: '1px solid var(--color-border)',
                borderLeft: `3px solid ${n.notification_type === 'PEST_ALERT' ? '#ef4444' : '#f59e0b'}`,
              }}>
                <span style={{ fontSize: '1.2rem' }}>
                  {n.notification_type === 'PEST_ALERT' ? '🐛' : '📊'}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--color-text-primary)' }}>{n.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{n.message}</div>
                </div>
                <span style={{ fontSize: '0.68rem', color: 'var(--color-text-secondary)', whiteSpace: 'nowrap' }}>
                  {new Date(n.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Two-column: Weather + Irrigation */}
      {weather && hasFields && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
          <WeatherCard weather={weather} />
          {irrigation && <IrrigationTimer irrigation={irrigation} />}
        </div>
      )}

      {/* Weather only (no fields yet) */}
      {weather && !hasFields && (
        <div style={{ marginBottom: '24px' }}>
          <WeatherCard weather={weather} />
        </div>
      )}

      {/* Soil Health */}
      {soil && hasFields && (
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
      )}

      {/* Crop Status */}
      {hasFields && activeField && <CropStatusBanner field={activeField} />}

      {/* Alerts Feed — derived from real data */}
      <AlertsFeed alerts={alerts} />

      {/* Empty State */}
      {!hasFields && (
        <div style={{
          textAlign: 'center', padding: '48px', borderRadius: '16px',
          border: '2px dashed var(--color-border)', background: 'var(--color-surface)', marginTop: '16px',
        }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>🌱</div>
          <h3 style={{ fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: '8px' }}>No farms added yet</h3>
          <p style={{ color: 'var(--color-text-secondary)', margin: '0 0 20px' }}>Add your first farm to start tracking crops and get better AI recommendations</p>
          <button
            onClick={() => navigate('/farms')}
            style={{
              padding: '12px 28px', background: 'var(--color-accent-primary)',
              color: '#fff', border: 'none', borderRadius: '12px',
              fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer',
            }}
          >
            Add Farm →
          </button>
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