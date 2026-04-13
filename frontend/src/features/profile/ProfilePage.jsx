import React, { useState } from 'react';
import { User, Plus, MapPin, Phone, Camera, ScanLine, Bell, BarChart2, Shield, Edit2, Map } from 'lucide-react';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { Modal } from '../../components/ui/Modal';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { useFieldStore } from '../../stores/useFieldStore.jsx';
import { AddFieldForm } from '../fields/components/AddFieldForm';
import { FieldMap } from '../fields/components/FieldMap';

const StatItem = ({ icon: Icon, label, value, color }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 0', borderBottom: '1px solid var(--color-border)' }}>
    <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
      <Icon size={17} color={color} />
    </div>
    <div>
      <div style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-text-primary)', lineHeight: 1.1 }}>{value}</div>
      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>{label}</div>
    </div>
  </div>
);

const ProfilePage = () => {
  const { farmer, user } = useUserStore();
  const { fields, addField, setActiveField, activeFieldId } = useFieldStore();
  const [showAddForm, setShowAddForm] = useState(false);
  const [showFieldMap, setShowFieldMap] = useState(false);
  const [selectedField, setSelectedField] = useState(null);
  const [notifications, setNotifications] = useState({ email: true, sms: true, weekly: false, ai: true });

  const handleAddField = (fieldData) => {
    const f = addField(fieldData);
    setShowAddForm(false);
    setActiveField(f.id);
  };

  const handleViewDetails = (field) => {
    setSelectedField(field);
    setShowFieldMap(true);
    setActiveField(field.id);
  };

  return (
    <PageWrapper>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.65rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
          My Profile
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: '4px 0 0' }}>
          Manage your farming details and fields
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: '24px', alignItems: 'start' }}>
        {/* LEFT SIDEBAR */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

          {/* Profile Card */}
          <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '24px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)', textAlign: 'center' }}>
            <div style={{ width: '72px', height: '72px', borderRadius: '50%', background: 'linear-gradient(135deg,#1A7A40,#FACC15)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px', boxShadow: '0 4px 16px rgba(26,122,64,0.3)', fontSize: '1.8rem', fontWeight: 800, color: '#fff', fontFamily: "'Plus Jakarta Sans',sans-serif" }}>
              {(farmer?.name?.[0] || 'F').toUpperCase()}
            </div>
            <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.15rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 6px' }}>
              {farmer?.name || 'Farmer'}
            </h2>
            {user?.email ? (
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.8rem', margin: '0 0 8px', wordBreak: 'break-all' }}>
                {user.email}
              </p>
            ) : null}
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.83rem', margin: '0 0 4px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px' }}>
              <MapPin size={13} /> {farmer?.location || farmer?.village || 'Location not set'}
            </p>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.83rem', margin: '0 0 16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px' }}>
              <Phone size={13} /> {farmer?.phone || '—'}
            </p>
            <button style={{ width: '100%', padding: '10px', borderRadius: '12px', border: '1.5px solid var(--color-accent-primary)', background: 'transparent', color: 'var(--color-accent-primary)', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
              <Edit2 size={15} /> Edit Profile
            </button>
          </div>

          {/* Farming Info */}
          <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 14px' }}>🌾 Farm Details</h3>
            {[
              { label: 'Farm Size', value: `${fields.reduce((s, f) => s + (parseFloat(f.area) || 0), 0) || 5} Acres` },
              { label: 'Primary Crops', value: fields.length > 0 ? fields.map(f => f.crop).slice(0, 2).join(', ') : 'Wheat, Rice' },
              { label: 'Soil Type', value: fields[0]?.soilType || 'Loamy' },
              { label: 'Total Fields', value: `${fields.length} field${fields.length !== 1 ? 's' : ''}` },
            ].map(item => (
              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border)', fontSize: '0.83rem' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>{item.label}</span>
                <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{item.value}</span>
              </div>
            ))}
          </div>

          {/* Stats */}
          <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 8px' }}>📊 Activity Stats</h3>
            <StatItem icon={Camera} label="Total Scans" value="42" color="#8B5CF6" />
            <StatItem icon={Shield} label="Pests Found" value="17" color="#DC2626" />
            <StatItem icon={Bell} label="Alerts Received" value="28" color="#F59E0B" />
          </div>

          {/* Notification Prefs */}
          <div style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 14px' }}>🔔 Notifications</h3>
            {[
              { key: 'email', label: 'Email Alerts' },
              { key: 'sms', label: 'SMS Alerts' },
              { key: 'weekly', label: 'Weekly Reports' },
              { key: 'ai', label: 'AI Recommendations' },
            ].map(item => (
              <div key={item.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '9px 0', borderBottom: '1px solid var(--color-border)' }}>
                <span style={{ fontSize: '0.83rem', color: 'var(--color-text-primary)', fontWeight: 500 }}>{item.label}</span>
                <button onClick={() => setNotifications(p => ({ ...p, [item.key]: !p[item.key] }))} style={{
                  width: '44px', height: '24px', borderRadius: '12px', border: 'none', cursor: 'pointer', position: 'relative', transition: 'background 0.2s',
                  background: notifications[item.key] ? 'var(--color-accent-primary)' : 'var(--color-border)',
                }}>
                  <span style={{
                    position: 'absolute', top: '3px', width: '18px', height: '18px', borderRadius: '50%', background: '#fff', transition: 'left 0.2s',
                    left: notifications[item.key] ? '23px' : '3px',
                    boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
                  }} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT MAIN */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
              My Sown Fields ({fields.length})
            </h2>
            <button onClick={() => setShowAddForm(true)} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', background: 'var(--color-accent-primary)', color: '#fff', border: 'none', borderRadius: '12px', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}>
              <Plus size={16} /> Add New Field
            </button>
          </div>

          {fields.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '64px 32px', background: '#fff', borderRadius: '20px', border: '2px dashed var(--color-border)' }}>
              <div style={{ fontSize: '3rem', marginBottom: '12px' }}>🌾</div>
              <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: '8px' }}>No fields added yet</h3>
              <p style={{ color: 'var(--color-text-secondary)', maxWidth: '300px', margin: '0 auto 20px', fontSize: '0.875rem' }}>
                Add fields to get personalized advisory and crop health updates
              </p>
              <button onClick={() => setShowAddForm(true)} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '12px 24px', background: 'var(--color-accent-primary)', color: '#fff', border: 'none', borderRadius: '12px', fontWeight: 600, cursor: 'pointer' }}>
                <Plus size={16} /> Add Field Details
              </button>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
              {fields.map(field => (
                <div key={field.id} style={{ background: '#fff', borderRadius: '20px', border: '1px solid var(--color-border)', overflow: 'hidden', boxShadow: '0 2px 12px rgba(0,0,0,0.06)', transition: 'transform 0.15s, box-shadow 0.15s', cursor: 'default' }}
                  onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.1)'; }}
                  onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.06)'; }}>
                  {/* Card Header */}
                  <div style={{ background: 'var(--color-section-header-bg)', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: 'var(--color-accent-primary)', fontSize: '0.95rem' }}>{field.name}</span>
                    {field.id === activeFieldId && (
                      <span style={{ background: 'var(--color-accent-primary)', color: '#fff', fontSize: '0.7rem', fontWeight: 700, padding: '2px 8px', borderRadius: '10px' }}>Active</span>
                    )}
                  </div>
                  {/* Card Body */}
                  <div style={{ padding: '16px 18px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '14px' }}>
                      {[
                        { label: 'Crop', value: field.crop || '—', icon: '🌾' },
                        { label: 'Area', value: `${field.area} ${field.areaUnit || 'acres'}`, icon: '📐' },
                        { label: 'Soil', value: field.soilType || '—', icon: '🪨' },
                        { label: 'Stage', value: field.growthStage || 'Vegetative', icon: '🌱' },
                      ].map(item => (
                        <div key={item.label} style={{ background: 'var(--color-bg-primary)', borderRadius: '10px', padding: '10px 12px' }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--color-text-secondary)', marginBottom: '3px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.icon} {item.label}</div>
                          <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', fontSize: '0.85rem' }}>{item.value}</div>
                        </div>
                      ))}
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={() => handleViewDetails(field)} style={{ flex: 1, padding: '9px', borderRadius: '10px', border: 'none', background: 'var(--color-accent-primary)', color: '#fff', fontWeight: 600, fontSize: '0.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
                        <Map size={14} /> View Map
                      </button>
                      {field.id !== activeFieldId && (
                        <button onClick={() => setActiveField(field.id)} style={{ flex: 1, padding: '9px', borderRadius: '10px', border: '1.5px solid var(--color-border)', background: 'transparent', color: 'var(--color-text-secondary)', fontWeight: 600, fontSize: '0.8rem', cursor: 'pointer' }}>
                          Set Active
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {/* Add More Card */}
              <div onClick={() => setShowAddForm(true)} style={{ background: 'transparent', borderRadius: '20px', border: '2px dashed var(--color-border)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 20px', cursor: 'pointer', transition: 'border-color 0.15s, background 0.15s', minHeight: '200px' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--color-accent-primary)'; e.currentTarget.style.background = 'var(--color-section-header-bg)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.background = 'transparent'; }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'var(--color-section-header-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '12px' }}>
                  <Plus size={22} color="var(--color-accent-primary)" />
                </div>
                <span style={{ fontWeight: 600, color: 'var(--color-accent-primary)', fontSize: '0.9rem' }}>Add New Field</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <Modal isOpen={showAddForm} onClose={() => setShowAddForm(false)} size="lg">
        <AddFieldForm onSubmit={handleAddField} onCancel={() => setShowAddForm(false)} />
      </Modal>
      <Modal isOpen={showFieldMap} onClose={() => setShowFieldMap(false)} title={selectedField?.name || 'Field Details'} size="xl">
        {selectedField && <FieldMap field={selectedField} onLocationUpdate={() => {}} />}
      </Modal>
    </PageWrapper>
  );
};

export { ProfilePage };
