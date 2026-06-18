import React, { useEffect, useState } from 'react';
import { useFarmStore } from '../../stores/useFarmStore';
import { useCropCycleStore } from '../../stores/useCropCycleStore';
import { PageWrapper } from '../../components/layout/PageWrapper';

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
  const [farmForm, setFarmForm] = useState({ farm_name: '', state: '', district: '', village: '', total_area: '', soil_type: 'LOAMY', irrigation_source: 'RAIN_FED' });
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
    setFarmForm({ farm_name: '', state: '', district: '', village: '', total_area: '', soil_type: 'LOAMY', irrigation_source: 'RAIN_FED' });
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
      irrigation_source: farm.irrigation_source || 'RAIN_FED',
    });
    setShowFarmForm(true);
  };

  const farmCycles = (farmId) => cycles.filter((c) => c.farm_id === farmId);

  return (
    <PageWrapper>
      <div className="max-w-[1200px] mx-auto transition-all duration-300">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="font-['Plus_Jakarta_Sans',sans-serif] text-2xl font-extrabold text-[var(--color-text-primary)]">
              🌾 My Farms
            </h1>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">
              Manage your farms and crop cycles
            </p>
          </div>
          <button 
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[var(--sidebar-bg)] to-[var(--color-accent-primary)] text-white font-bold text-sm cursor-pointer shadow-md hover:shadow-lg active:scale-95 transition-all duration-150"
            onClick={() => { setShowFarmForm(true); setEditingFarm(null); setFarmForm({ farm_name: '', state: '', district: '', village: '', total_area: '', soil_type: 'LOAMY', irrigation_source: 'RAIN_FED' }); }}
          >
            + Add Farm
          </button>
        </div>

        {/* Farm Form Modal */}
        {showFarmForm && (
          <div 
            className="fixed inset-0 bg-[rgba(10,25,15,0.55)] flex items-center justify-center z-[1000] backdrop-blur-md transition-all duration-200"
            onClick={() => setShowFarmForm(false)}
          >
            <form 
              className="bg-[var(--color-bg-secondary)] rounded-3xl p-8 w-[92%] max-w-[540px] shadow-2xl border border-[var(--color-border)] max-h-[85vh] overflow-y-auto transition-transform duration-300 ease-out" 
              onClick={(e) => e.stopPropagation()} 
              onSubmit={handleFarmSubmit}
            >
              <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-xl font-extrabold text-[var(--color-text-primary)] mb-6 border-b border-[var(--color-border)] pb-3">
                {editingFarm ? 'Edit Farm' : 'Add New Farm'}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5 col-span-2">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Farm Name *</label>
                  <input 
                    required 
                    value={farmForm.farm_name} 
                    onChange={(e) => setFarmForm({ ...farmForm, farm_name: e.target.value })} 
                    placeholder="e.g. North Field" 
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">State</label>
                  <input 
                    value={farmForm.state} 
                    onChange={(e) => setFarmForm({ ...farmForm, state: e.target.value })} 
                    placeholder="Madhya Pradesh" 
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">District</label>
                  <input 
                    value={farmForm.district} 
                    onChange={(e) => setFarmForm({ ...farmForm, district: e.target.value })} 
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Village</label>
                  <input 
                    value={farmForm.village} 
                    onChange={(e) => setFarmForm({ ...farmForm, village: e.target.value })} 
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Total Area (acres)</label>
                  <input 
                    type="number" 
                    step="0.1" 
                    value={farmForm.total_area} 
                    onChange={(e) => setFarmForm({ ...farmForm, total_area: e.target.value })} 
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Soil Type</label>
                  <select 
                    value={farmForm.soil_type} 
                    onChange={(e) => setFarmForm({ ...farmForm, soil_type: e.target.value })}
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  >
                    {SOIL_TYPES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Irrigation</label>
                  <select 
                    value={farmForm.irrigation_source} 
                    onChange={(e) => setFarmForm({ ...farmForm, irrigation_source: e.target.value })}
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  >
                    {IRRIGATION_TYPES.map((i) => <option key={i} value={i}>{i}</option>)}
                  </select>
                </div>
              </div>
              <div className="flex gap-3 justify-end mt-7">
                <button type="button" className="px-6 py-2.5 rounded-xl border border-[var(--color-border)] bg-transparent text-[var(--color-text-secondary)] font-semibold text-sm cursor-pointer hover:bg-[var(--color-bg-primary)] hover:text-[var(--color-text-primary)] transition-all duration-150" onClick={() => setShowFarmForm(false)}>Cancel</button>
                <button type="submit" className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[var(--sidebar-bg)] to-[var(--color-accent-primary)] text-white font-bold text-sm cursor-pointer shadow-md hover:shadow-lg hover:brightness-105 active:scale-95 transition-all duration-150">{editingFarm ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        )}

        {/* Crop Form Modal */}
        {showCropForm && (
          <div 
            className="fixed inset-0 bg-[rgba(10,25,15,0.55)] flex items-center justify-center z-[1000] backdrop-blur-md transition-all duration-200"
            onClick={() => setShowCropForm(null)}
          >
            <form 
              className="bg-[var(--color-bg-secondary)] rounded-3xl p-8 w-[92%] max-w-[540px] shadow-2xl border border-[var(--color-border)] max-h-[85vh] overflow-y-auto transition-transform duration-300 ease-out" 
              onClick={(e) => e.stopPropagation()} 
              onSubmit={handleCropSubmit}
            >
              <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-xl font-extrabold text-[var(--color-text-primary)] mb-6 border-b border-[var(--color-border)] pb-3">Add Crop Cycle</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5 col-span-2">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Crop Name *</label>
                  <input 
                    required 
                    value={cropForm.crop_name} 
                    onChange={(e) => setCropForm({ ...cropForm, crop_name: e.target.value })} 
                    placeholder="e.g. Soybean" 
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Variety</label>
                  <input 
                    value={cropForm.crop_variety} 
                    onChange={(e) => setCropForm({ ...cropForm, crop_variety: e.target.value })} 
                    placeholder="e.g. JS-95-60" 
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Season</label>
                  <select 
                    value={cropForm.season} 
                    onChange={(e) => setCropForm({ ...cropForm, season: e.target.value })}
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  >
                    {CROP_SEASONS.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Sowing Date</label>
                  <input 
                    type="date" 
                    value={cropForm.sowing_date} 
                    onChange={(e) => setCropForm({ ...cropForm, sowing_date: e.target.value })} 
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-wider">Area (acres)</label>
                  <input 
                    type="number" 
                    step="0.1" 
                    value={cropForm.area_under_crop} 
                    onChange={(e) => setCropForm({ ...cropForm, area_under_crop: e.target.value })} 
                    className="px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] text-sm outline-none hover:border-[var(--color-accent-primary)] focus:border-[var(--color-accent-primary)] focus:bg-[var(--color-bg-secondary)] focus:ring-4 focus:ring-green-400/15 transition-all"
                  />
                </div>
              </div>
              <div className="flex gap-3 justify-end mt-7">
                <button type="button" className="px-6 py-2.5 rounded-xl border border-[var(--color-border)] bg-transparent text-[var(--color-text-secondary)] font-semibold text-sm cursor-pointer hover:bg-[var(--color-bg-primary)] hover:text-[var(--color-text-primary)] transition-all duration-150" onClick={() => setShowCropForm(null)}>Cancel</button>
                <button type="submit" className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[var(--sidebar-bg)] to-[var(--color-accent-primary)] text-white font-bold text-sm cursor-pointer shadow-md hover:shadow-lg hover:brightness-105 active:scale-95 transition-all duration-150">Add Crop</button>
              </div>
            </form>
          </div>
        )}

        {/* Farm Cards */}
        {loading ? (
          <div className="text-center py-16 text-[var(--color-text-secondary)] text-sm font-semibold flex items-center justify-center gap-3">
            <div className="w-5 h-5 border-3 border-green-200 border-t-[var(--color-accent-primary)] rounded-full animate-spin" />
            Loading farms...
          </div>
        ) : farms.length === 0 ? (
          <div className="text-center py-20 px-8 bg-[var(--color-bg-secondary)] rounded-3xl border-2 border-dashed border-[var(--color-border)] shadow-sm">
            <span className="text-5xl block mb-4">🏡</span>
            <h3 className="font-['Plus_Jakarta_Sans',sans-serif] font-bold text-[var(--color-text-primary)] mb-2 text-xl">No farms yet</h3>
            <p className="text-[var(--color-text-secondary)] text-sm max-w-[340px] mx-auto mb-6">Add your first farm to start tracking crops and get better AI recommendations.</p>
            <button 
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[var(--sidebar-bg)] to-[var(--color-accent-primary)] text-white font-bold text-sm cursor-pointer shadow-md hover:shadow-lg transition-all duration-150"
              onClick={() => { setShowFarmForm(true); setEditingFarm(null); setFarmForm({ farm_name: '', state: '', district: '', village: '', total_area: '', soil_type: 'LOAMY', irrigation_source: 'RAIN_FED' }); }}
            >
              + Add Your First Farm
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            {farms.map((farm) => {
              const fCycles = farmCycles(farm.id);
              const activeCycles = fCycles.filter((c) => c.status === 'ACTIVE');
              const isExpanded = expandedFarm === farm.id;
              return (
                <div key={farm.id} className="bg-[var(--color-bg-secondary)] rounded-2xl border border-[var(--color-border)] shadow-sm hover:shadow-md hover:-translate-y-0.5 hover:border-[var(--color-accent-primary)] transition-all duration-250 ease-out overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between p-5 sm:px-7 sm:py-5 cursor-pointer select-none hover:bg-[var(--color-surface-hover)] transition-colors duration-200" onClick={() => setExpandedFarm(isExpanded ? null : farm.id)}>
                    <div className="flex flex-col">
                      <h3 className="font-['Plus_Jakarta_Sans',sans-serif] text-lg font-bold text-[var(--color-text-primary)] mb-1 sm:mb-1.5">{farm.farm_name}</h3>
                      <div className="flex flex-wrap gap-2.5 items-center">
                        {farm.village && <span className="text-xs text-[var(--color-text-secondary)] flex items-center gap-1">📍 {farm.village}</span>}
                        {farm.total_area && <span className="text-xs text-[var(--color-text-secondary)] flex items-center gap-1">📐 {farm.total_area} acres</span>}
                        <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[var(--color-warning-bg)] text-[var(--color-warning-text)] border border-[var(--color-warning-border)]">{farm.soil_type}</span>
                        <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[rgba(26,122,64,0.08)] text-[var(--color-accent-primary)] border border-[rgba(26,122,64,0.15)]">{farm.irrigation_source}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 mt-3 sm:mt-0">
                      <span className="bg-[var(--color-success-bg)] text-[var(--color-success-text)] px-3.5 py-1 rounded-full text-[11px] font-bold">{activeCycles.length} active</span>
                      <span className={`text-xs text-[var(--color-text-secondary)] transition-transform duration-200 ${isExpanded ? 'rotate-180 text-[var(--color-accent-primary)]' : ''}`}>▼</span>
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="p-6 sm:px-7 sm:pb-6 border-t border-dashed border-[var(--color-border)] bg-[rgba(26,122,64,0.005)] transition-all">
                      <div className="flex gap-2.5 mb-5">
                        <button className="px-3.5 py-1.5 rounded-lg text-xs font-semibold border border-[var(--color-border)] bg-[var(--color-bg-secondary)] text-[var(--color-text-primary)] hover:border-[var(--color-accent-primary)] hover:text-[var(--color-accent-primary)] hover:bg-[var(--color-surface-hover)] transition-all" onClick={() => startEdit(farm)}>✏️ Edit</button>
                        <button className="px-3.5 py-1.5 rounded-lg text-xs font-semibold border border-[var(--color-border)] bg-[var(--color-bg-secondary)] text-[var(--color-text-primary)] hover:border-[var(--color-accent-primary)] hover:text-[var(--color-accent-primary)] hover:bg-[var(--color-surface-hover)] transition-all" onClick={() => setShowCropForm(farm.id)}>🌱 Add Crop</button>
                        <button className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-[var(--color-danger-bg)] text-[var(--color-danger)] hover:brightness-95 hover:shadow transition-all" onClick={() => { if (confirm('Delete this farm?')) deleteFarm(farm.id); }}>🗑️ Delete</button>
                      </div>

                      {activeCycles.length === 0 ? (
                        <p className="text-xs text-[var(--color-text-secondary)] italic pt-2">No active crops. Add one to start tracking.</p>
                      ) : (
                        <div className="flex flex-col gap-4 mt-2">
                          {activeCycles.map((cycle) => (
                            <div key={cycle.id} className="bg-[var(--color-bg-primary)] rounded-2xl p-4 sm:p-5 border border-[var(--color-border)] hover:border-[var(--color-accent-primary)] transition-colors duration-200">
                              <div className="flex items-center justify-between mb-4">
                                <div>
                                  <strong className="text-[15px] font-bold text-[var(--color-text-primary)]">{cycle.crop_name}</strong>
                                  {cycle.crop_variety && <span className="ml-2 text-[10px] font-bold px-2 py-0.5 rounded bg-[rgba(124,58,237,0.08)] text-[#7c3aed] border border-[rgba(124,58,237,0.15)]">{cycle.crop_variety}</span>}
                                </div>
                                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[var(--color-warning-bg)] text-[var(--color-warning-text)] border border-[var(--color-warning-border)]">{cycle.season}</span>
                              </div>
                              <div className="flex flex-wrap gap-2 mb-4 bg-[var(--color-bg-secondary)] p-2 rounded-xl border border-[var(--color-border)]">
                                {CROP_STAGES.map((stage, idx) => {
                                  const currentIdx = CROP_STAGES.indexOf(cycle.current_stage);
                                  const isDone = idx <= currentIdx;
                                  const isCurrent = idx === currentIdx;
                                  return (
                                    <div
                                      key={stage}
                                      className={`flex-1 h-9 rounded-lg flex items-center justify-center cursor-pointer transition-all duration-200 border ${isDone ? 'border-transparent text-white' : 'border-[var(--color-border)] text-[var(--color-text-secondary)]'} ${isCurrent ? 'scale-[1.03] shadow-md border-transparent ring-2 ring-[var(--color-accent-primary)]/20' : ''}`}
                                      style={isDone ? { backgroundColor: STAGE_COLORS[stage] } : {}}
                                      title={stage}
                                      onClick={() => {
                                        if (idx === currentIdx + 1) updateStage(cycle.id, stage);
                                      }}
                                    >
                                      <span className="text-[9px] font-extrabold uppercase tracking-wider">{stage.slice(0, 3)}</span>
                                    </div>
                                  );
                                })}
                              </div>
                              <div className="flex items-center justify-between gap-4 flex-wrap text-xs text-[var(--color-text-secondary)] border-t border-[var(--color-border)] pt-3 mt-1">
                                <div className="flex gap-4">
                                  {cycle.sowing_date && <span>🌱 Sown: {cycle.sowing_date}</span>}
                                  {cycle.area_under_crop && <span>📐 {cycle.area_under_crop} ac</span>}
                                </div>
                                {cycle.current_stage === 'HARVESTED' ? null : (
                                  <button className="px-3 py-1.5 rounded-lg text-xs font-bold bg-[var(--color-success-bg)] text-[var(--color-success-text)] hover:brightness-95 hover:shadow transition-all" onClick={() => completeCycle(cycle.id)}>
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
    </PageWrapper>
  );
}
