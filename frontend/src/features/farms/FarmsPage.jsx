import React, { useEffect, useState } from 'react';
import { useFarmStore } from '../../stores/useFarmStore';
import { useCropCycleStore } from '../../stores/useCropCycleStore';
import './FarmsPage.css';

const SOIL_TYPES = ['ALLUVIAL', 'BLACK', 'RED', 'LATERITE', 'SANDY', 'CLAYEY', 'LOAMY', 'OTHER'];
const IRRIGATION_TYPES = ['BOREWELL', 'CANAL', 'RAIN_FED', 'DRIP', 'SPRINKLER', 'OTHER'];
const CROP_STAGES = ['SEEDING', 'GERMINATION', 'VEGETATIVE', 'FLOWERING', 'FRUITING', 'MATURITY', 'HARVEST_READY'];
const CROP_SEASONS = ['KHARIF', 'RABI', 'ZAID'];

const STAGE_COLORS = {
  SEEDING: '#10b981', GERMINATION: '#34d399', VEGETATIVE: '#22c55e',
  FLOWERING: '#f59e0b', FRUITING: '#f97316', MATURITY: '#ef4444', HARVEST_READY: '#6b7280',
};

export function FarmsPage() {
  const { farms, loading, fetchFarms, createFarm, updateFarm, deleteFarm } = useFarmStore();
  const { cycles, fetchCycles, createCycle, updateStage, completeCycle } = useCropCycleStore();
  const [showFarmForm, setShowFarmForm] = useState(false);
  const [showCropForm, setShowCropForm] = useState(null); // farmId or null
  const [editingFarm, setEditingFarm] = useState(null);
  const [expandedFarm, setExpandedFarm] = useState(null);
  const [farmForm, setFarmForm] = useState({ farm_name: '', state: '', district: '', village: '', total_area: '', soil_type: 'LOAMY', irrigation_source: 'RAINFED' });
  const [cropForm, setCropForm] = useState({ crop_name: '', crop_variety: '', season: 'KHARIF', sowing_date: '', area_under_crop: '' });

  useEffect(() => { fetchFarms(); fetchCycles(); }, []);

  const handleFarmSubmit = async (e) => {
    e.preventDefault();
    const data = { ...farmForm, total_area: farmForm.total_area ? parseFloat(farmForm.total_area) : null };
    if (editingFarm) {
      await updateFarm(editingFarm.id, data);
    } else {
      await createFarm(data);
    }
    setShowFarmForm(false);
    setEditingFarm(null);
    setFarmForm({ farm_name: '', state: '', district: '', village: '', total_area: '', soil_type: 'LOAMY', irrigation_source: 'RAINFED' });
  };

  const handleCropSubmit = async (e) => {
    e.preventDefault();
    await createCycle({
      farm_id: showCropForm,
      ...cropForm,
      year: new Date().getFullYear(),
      area_under_crop: cropForm.area_under_crop ? parseFloat(cropForm.area_under_crop) : null,
      sowing_date: cropForm.sowing_date || null,
    });
    setShowCropForm(null);
    setCropForm({ crop_name: '', crop_variety: '', season: 'KHARIF', sowing_date: '', area_under_crop: '' });
    fetchCycles();
  };

  const startEdit = (farm) => {
    setEditingFarm(farm);
    setFarmForm({
      farm_name: farm.farm_name,
      state: farm.state || '',
      district: farm.district || '',
      village: farm.village || '',
      total_area: farm.total_area || '',
      soil_type: farm.soil_type || 'LOAMY',
      irrigation_source: farm.irrigation_source || 'RAINFED',
    });
    setShowFarmForm(true);
  };

  const farmCycles = (farmId) => cycles.filter((c) => c.farm_id === farmId);

  return (
    <div className="farms-page">
      <div className="farms-header">
        <div>
          <h1>🌾 My Farms</h1>
          <p className="farms-subtitle">Manage your farms and crop cycles</p>
        </div>
        <button className="btn-primary" onClick={() => { setShowFarmForm(true); setEditingFarm(null); setFarmForm({ farm_name: '', state: '', district: '', village: '', total_area: '', soil_type: 'LOAMY', irrigation_source: 'RAINFED' }); }}>
          + Add Farm
        </button>
      </div>

      {/* Farm Form Modal */}
      {showFarmForm && (
        <div className="modal-overlay" onClick={() => setShowFarmForm(false)}>
          <form className="modal-card" onClick={(e) => e.stopPropagation()} onSubmit={handleFarmSubmit}>
            <h2>{editingFarm ? 'Edit Farm' : 'Add New Farm'}</h2>
            <div className="form-grid">
              <div className="form-group">
                <label>Farm Name *</label>
                <input required value={farmForm.farm_name} onChange={(e) => setFarmForm({ ...farmForm, farm_name: e.target.value })} placeholder="e.g. North Field" />
              </div>
              <div className="form-group">
                <label>State</label>
                <input value={farmForm.state} onChange={(e) => setFarmForm({ ...farmForm, state: e.target.value })} placeholder="Madhya Pradesh" />
              </div>
              <div className="form-group">
                <label>District</label>
                <input value={farmForm.district} onChange={(e) => setFarmForm({ ...farmForm, district: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Village</label>
                <input value={farmForm.village} onChange={(e) => setFarmForm({ ...farmForm, village: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Total Area (acres)</label>
                <input type="number" step="0.1" value={farmForm.total_area} onChange={(e) => setFarmForm({ ...farmForm, total_area: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Soil Type</label>
                <select value={farmForm.soil_type} onChange={(e) => setFarmForm({ ...farmForm, soil_type: e.target.value })}>
                  {SOIL_TYPES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Irrigation</label>
                <select value={farmForm.irrigation_source} onChange={(e) => setFarmForm({ ...farmForm, irrigation_source: e.target.value })}>
                  {IRRIGATION_TYPES.map((i) => <option key={i} value={i}>{i}</option>)}
                </select>
              </div>
            </div>
            <div className="form-actions">
              <button type="button" className="btn-ghost" onClick={() => setShowFarmForm(false)}>Cancel</button>
              <button type="submit" className="btn-primary">{editingFarm ? 'Update' : 'Create'}</button>
            </div>
          </form>
        </div>
      )}

      {/* Crop Form Modal */}
      {showCropForm && (
        <div className="modal-overlay" onClick={() => setShowCropForm(null)}>
          <form className="modal-card" onClick={(e) => e.stopPropagation()} onSubmit={handleCropSubmit}>
            <h2>Add Crop Cycle</h2>
            <div className="form-grid">
              <div className="form-group">
                <label>Crop Name *</label>
                <input required value={cropForm.crop_name} onChange={(e) => setCropForm({ ...cropForm, crop_name: e.target.value })} placeholder="e.g. Soybean" />
              </div>
              <div className="form-group">
                <label>Variety</label>
                <input value={cropForm.crop_variety} onChange={(e) => setCropForm({ ...cropForm, crop_variety: e.target.value })} placeholder="e.g. JS-95-60" />
              </div>
              <div className="form-group">
                <label>Season</label>
                <select value={cropForm.season} onChange={(e) => setCropForm({ ...cropForm, season: e.target.value })}>
                  {CROP_SEASONS.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Sowing Date</label>
                <input type="date" value={cropForm.sowing_date} onChange={(e) => setCropForm({ ...cropForm, sowing_date: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Area (acres)</label>
                <input type="number" step="0.1" value={cropForm.area_under_crop} onChange={(e) => setCropForm({ ...cropForm, area_under_crop: e.target.value })} />
              </div>
            </div>
            <div className="form-actions">
              <button type="button" className="btn-ghost" onClick={() => setShowCropForm(null)}>Cancel</button>
              <button type="submit" className="btn-primary">Add Crop</button>
            </div>
          </form>
        </div>
      )}

      {/* Farm Cards */}
      {loading ? (
        <div className="loading-state">Loading farms...</div>
      ) : farms.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">🏡</span>
          <h3>No farms yet</h3>
          <p>Add your first farm to start tracking crops and get better AI recommendations.</p>
        </div>
      ) : (
        <div className="farms-grid">
          {farms.map((farm) => {
            const fCycles = farmCycles(farm.id);
            const activeCycles = fCycles.filter((c) => c.status === 'ACTIVE');
            const isExpanded = expandedFarm === farm.id;
            return (
              <div key={farm.id} className={`farm-card ${isExpanded ? 'expanded' : ''}`}>
                <div className="farm-card-header" onClick={() => setExpandedFarm(isExpanded ? null : farm.id)}>
                  <div className="farm-info">
                    <h3>{farm.farm_name}</h3>
                    <div className="farm-meta">
                      {farm.village && <span>📍 {farm.village}</span>}
                      {farm.total_area && <span>📐 {farm.total_area} acres</span>}
                      <span className="soil-badge">{farm.soil_type}</span>
                      <span className="irrigation-badge">{farm.irrigation_source}</span>
                    </div>
                  </div>
                  <div className="farm-stats">
                    <span className="active-count">{activeCycles.length} active</span>
                    <span className={`expand-icon ${isExpanded ? 'rotated' : ''}`}>▼</span>
                  </div>
                </div>

                {isExpanded && (
                  <div className="farm-card-body">
                    <div className="farm-actions">
                      <button className="btn-sm btn-outline" onClick={() => startEdit(farm)}>✏️ Edit</button>
                      <button className="btn-sm btn-outline" onClick={() => setShowCropForm(farm.id)}>🌱 Add Crop</button>
                      <button className="btn-sm btn-danger" onClick={() => { if (confirm('Delete this farm?')) deleteFarm(farm.id); }}>🗑️</button>
                    </div>

                    {activeCycles.length === 0 ? (
                      <p className="no-crops">No active crops. Add one to start tracking.</p>
                    ) : (
                      <div className="crop-list">
                        {activeCycles.map((cycle) => (
                          <div key={cycle.id} className="crop-card">
                            <div className="crop-header">
                              <div>
                                <strong>{cycle.crop_name}</strong>
                                {cycle.crop_variety && <span className="variety-badge">{cycle.crop_variety}</span>}
                              </div>
                              <span className="season-tag">{cycle.season}</span>
                            </div>
                            <div className="stage-tracker">
                              {CROP_STAGES.map((stage, idx) => {
                                const currentIdx = CROP_STAGES.indexOf(cycle.current_stage);
                                const isDone = idx <= currentIdx;
                                const isCurrent = idx === currentIdx;
                                return (
                                  <div
                                    key={stage}
                                    className={`stage-dot ${isDone ? 'done' : ''} ${isCurrent ? 'current' : ''}`}
                                    style={isDone ? { backgroundColor: STAGE_COLORS[stage] } : {}}
                                    title={stage}
                                    onClick={() => {
                                      if (idx === currentIdx + 1) updateStage(cycle.id, stage);
                                    }}
                                  >
                                    <span className="stage-label">{stage.slice(0, 3)}</span>
                                  </div>
                                );
                              })}
                            </div>
                            <div className="crop-footer">
                              {cycle.sowing_date && <span>🌱 Sown: {cycle.sowing_date}</span>}
                              {cycle.area_under_crop && <span>📐 {cycle.area_under_crop}ac</span>}
                              {cycle.current_stage === 'HARVESTED' ? null : (
                                <button className="btn-sm btn-complete" onClick={() => completeCycle(cycle.id)}>
                                  ✅ Complete
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
