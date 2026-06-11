import React, { useState } from 'react';
import { User, Plus, MapPin, Phone, Camera, ScanLine, Bell, BarChart2, Shield, Edit2, Map, X } from 'lucide-react';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { Modal } from '../../components/ui/Modal';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { useFieldStore } from '../../stores/useFieldStore.jsx';
import { AddFieldForm } from '../fields/components/AddFieldForm';
import { FieldMap } from '../fields/components/FieldMap';

const ProfilePage = () => {
  const { farmer, user, updateFarmerProfile } = useUserStore();
  const { fields, addField, setActiveField, activeFieldId, getTotalLand, getUniqueCrops } = useFieldStore();
  
  // Modals state
  const [showAddForm, setShowAddForm] = useState(false);
  const [showFieldMap, setShowFieldMap] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);
  
  const [selectedField, setSelectedField] = useState(null);

  // Edit profile form state
  const [profileForm, setProfileForm] = useState({
    full_name: farmer?.name || user?.name || '',
    age: farmer?.age || '',
    gender: farmer?.gender || '',
    state: farmer?.state || '',
    district: farmer?.district || '',
    village: farmer?.village || '',
    farm_size_acres: farmer?.land_size_acres || '',
    annual_income: farmer?.annual_income || '',
    category: farmer?.category || '',
    preferred_language: farmer?.preferred_language || 'ENGLISH',
    soil_type: farmer?.soil_type || '',
    irrigation_source: farmer?.irrigation_source || ''
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

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

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveError(null);
    try {
      const updates = {
        ...profileForm,
        age: profileForm.age ? parseInt(profileForm.age) : null,
        farm_size_acres: profileForm.farm_size_acres ? parseFloat(profileForm.farm_size_acres) : null,
        annual_income: profileForm.annual_income ? parseFloat(profileForm.annual_income) : null,
      };
      
      // Filter out empty strings for enums
      if (!updates.gender) delete updates.gender;
      if (!updates.soil_type) delete updates.soil_type;
      if (!updates.irrigation_source) delete updates.irrigation_source;

      await updateFarmerProfile(updates);
      setShowEditProfile(false);
    } catch (err) {
      setSaveError(err?.message || 'Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
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
          <div style={{ background: 'var(--color-surface)', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '24px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)', textAlign: 'center' }}>
            <div style={{ width: '72px', height: '72px', borderRadius: '50%', background: 'linear-gradient(135deg,#1A7A40,#FACC15)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px', boxShadow: '0 4px 16px rgba(26,122,64,0.3)', fontSize: '1.8rem', fontWeight: 800, color: '#fff', fontFamily: "'Plus Jakarta Sans',sans-serif" }}>
              {(user?.name?.[0] || farmer?.name?.[0] || 'F').toUpperCase()}
            </div>
            <h2 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '1.15rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 6px' }}>
              {farmer?.full_name || user?.name || farmer?.name || 'Farmer'}
            </h2>
            {user?.email && (
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.8rem', margin: '0 0 8px', wordBreak: 'break-all' }}>
                {user.email}
              </p>
            )}
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.83rem', margin: '0 0 4px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px' }}>
              <MapPin size={13} /> {farmer?.state ? `${farmer.district || farmer.village}, ${farmer.state}` : 'Location not set'}
            </p>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.83rem', margin: '0 0 16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px' }}>
              <Phone size={13} /> {user?.phone_number || user?.phone || farmer?.phone || '—'}
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
               <div style={{ background: 'var(--color-bg-primary)', padding: '8px', borderRadius: '10px' }}>
                 <div style={{ fontSize: '0.65rem', color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>Age</div>
                 <div style={{ fontSize: '0.85rem', fontWeight: 700 }}>{farmer?.age || '—'}</div>
               </div>
               <div style={{ background: 'var(--color-bg-primary)', padding: '8px', borderRadius: '10px' }}>
                 <div style={{ fontSize: '0.65rem', color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>Gender</div>
                 <div style={{ fontSize: '0.85rem', fontWeight: 700 }}>{farmer?.gender || '—'}</div>
               </div>
            </div>
            <button 
              onClick={() => {
                setProfileForm({
                  full_name: farmer?.full_name || user?.name || farmer?.name || '',
                  age: farmer?.age || '',
                  gender: farmer?.gender || '',
                  state: farmer?.state || '',
                  district: farmer?.district || '',
                  village: farmer?.village || '',
                  farm_size_acres: farmer?.farm_size_acres || farmer?.land_size_acres || '',
                  annual_income: farmer?.annual_income || '',
                  category: farmer?.category || '',
                  preferred_language: farmer?.preferred_language || 'ENGLISH',
                  soil_type: farmer?.soil_type || '',
                  irrigation_source: farmer?.irrigation_source || ''
                });
                setShowEditProfile(true);
              }}
              style={{ width: '100%', padding: '10px', borderRadius: '12px', border: '1.5px solid var(--color-accent-primary)', background: 'transparent', color: 'var(--color-accent-primary)', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            >
              <Edit2 size={15} /> Edit Profile
            </button>
          </div>

          {/* Account Details from Backend */}
          <div style={{ background: 'var(--color-surface)', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 14px' }}>🛡️ Account Info</h3>
            {[
              { label: 'Status', value: user?.account_status || 'ACTIVE', highlight: user?.account_status === 'ACTIVE' },
              { label: 'Role', value: user?.role || 'FARMER' },
              { label: 'Joined', value: user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—' },
            ].map(item => (
              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border)', fontSize: '0.83rem' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>{item.label}</span>
                <span style={{ fontWeight: 600, color: item.highlight ? 'var(--color-success)' : 'var(--color-text-primary)' }}>{item.value}</span>
              </div>
            ))}
          </div>

          {/* Farming Info */}
          <div style={{ background: 'var(--color-surface)', borderRadius: '20px', border: '1px solid var(--color-border)', padding: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
            <h3 style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 14px' }}>🌾 Farm Details</h3>
            {[
              { label: 'Total Land', value: `${farmer?.farm_size_acres || farmer?.land_size_acres || getTotalLand() || 0} Acres` },
              { label: 'Soil Type', value: farmer?.soil_type || '—' },
              { label: 'Irrigation', value: farmer?.irrigation_source || '—' },
              { label: 'Language', value: farmer?.preferred_language || 'ENGLISH' },
              { label: 'Category', value: farmer?.category || 'Marginal' },
              { label: 'Annual Income', value: farmer?.annual_income ? `₹${Number(farmer.annual_income).toLocaleString('en-IN')}` : '—' },
            ].map(item => (
              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border)', fontSize: '0.83rem' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>{item.label}</span>
                <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{item.value}</span>
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
            <div style={{ textAlign: 'center', padding: '64px 32px', background: 'var(--color-surface)', borderRadius: '20px', border: '2px dashed var(--color-border)' }}>
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
                <div key={field.id} style={{ background: 'var(--color-surface)', borderRadius: '20px', border: '1px solid var(--color-border)', overflow: 'hidden', boxShadow: '0 2px 12px rgba(0,0,0,0.06)', transition: 'transform 0.15s, box-shadow 0.15s', cursor: 'default' }}
                  onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.1)'; }}
                  onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.06)'; }}>
                  {/* Card Header */}
                  <div style={{ background: 'var(--color-section-header-bg)', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontFamily: "'Plus Jakarta Sans',sans-serif", fontWeight: 700, color: 'var(--color-accent-primary)', fontSize: '0.95rem' }}>{field.name}</span>
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

      {/* Edit Profile Modal */}
      <Modal isOpen={showEditProfile} onClose={() => setShowEditProfile(false)} title="Edit Farmer Profile" size="lg">
        <form onSubmit={handleProfileSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '10px' }}>
          {saveError && (
            <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(220,38,38,0.1)', color: 'var(--color-error)', border: '1px solid var(--color-error)' }}>
              {saveError}
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Full Name</label>
              <input 
                type="text" 
                name="full_name"
                value={profileForm.full_name}
                onChange={handleProfileChange}
                required
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Age</label>
              <input 
                type="number" 
                name="age"
                value={profileForm.age}
                onChange={handleProfileChange}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Gender</label>
              <select 
                name="gender"
                value={profileForm.gender}
                onChange={handleProfileChange}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              >
                <option value="">Select Gender</option>
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Preferred Language</label>
              <select 
                name="preferred_language"
                value={profileForm.preferred_language}
                onChange={handleProfileChange}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              >
                <option value="ENGLISH">English</option>
                <option value="HINDI">Hindi</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>State</label>
              <input 
                type="text" 
                name="state"
                value={profileForm.state}
                onChange={handleProfileChange}
                required
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>District</label>
              <input 
                type="text" 
                name="district"
                value={profileForm.district}
                onChange={handleProfileChange}
                required
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Village</label>
              <input 
                type="text" 
                name="village"
                value={profileForm.village}
                onChange={handleProfileChange}
                required
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Land Size (Acres)</label>
              <input 
                type="number" 
                step="0.01"
                name="farm_size_acres"
                value={profileForm.farm_size_acres}
                onChange={handleProfileChange}
                required
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Annual Income (₹)</label>
              <input 
                type="number" 
                name="annual_income"
                value={profileForm.annual_income}
                onChange={handleProfileChange}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Soil Type</label>
              <select 
                name="soil_type"
                value={profileForm.soil_type}
                onChange={handleProfileChange}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              >
                <option value="">Select Soil Type</option>
                <option value="CLAY">Clay</option>
                <option value="LOAMY">Loamy</option>
                <option value="SANDY">Sandy</option>
                <option value="BLACK">Black</option>
                <option value="RED">Red</option>
                <option value="SILT">Silt</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Irrigation Source</label>
              <select 
                name="irrigation_source"
                value={profileForm.irrigation_source}
                onChange={handleProfileChange}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
              >
                <option value="">Select Irrigation Source</option>
                <option value="RAINFED">Rainfed</option>
                <option value="BOREWELL">Borewell</option>
                <option value="CANAL">Canal</option>
                <option value="DRIP">Drip</option>
                <option value="SPRINKLER">Sprinkler</option>
              </select>
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>Farmer Category</label>
            <input 
              type="text" 
              name="category"
              value={profileForm.category}
              onChange={handleProfileChange}
              placeholder="e.g. Marginal, Small"
              style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '10px' }}>
            <button 
              type="button" 
              onClick={() => setShowEditProfile(false)}
              style={{ padding: '10px 20px', borderRadius: '8px', border: '1px solid var(--color-border)', background: 'transparent', color: 'var(--color-text-secondary)', fontWeight: 600, cursor: 'pointer' }}
            >
              Cancel
            </button>
            <button 
              type="submit"
              disabled={isSaving}
              style={{ padding: '10px 20px', borderRadius: '8px', border: 'none', background: 'var(--color-accent-primary)', color: '#fff', fontWeight: 600, cursor: isSaving ? 'not-allowed' : 'pointer' }}
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </Modal>
    </PageWrapper>
  );
};

export { ProfilePage };
