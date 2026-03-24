import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MapPin,
  Plus,
  Sprout,
  Ruler,
  Layers,
  Navigation,
  X,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { CROP_TYPES, SOIL_TYPES } from '../../../lib/constants.jsx';

/* ── Styled input wrapper ─────────────────────────────── */
const InputGroup = ({ icon: Icon, label, error, children }) => (
  <div className="space-y-1.5">
    <label className="flex items-center gap-2 text-sm font-semibold text-green-800">
      {Icon && (
        <span
          className="w-6 h-6 rounded-md flex items-center justify-center"
          style={{ background: '#dcfce7' }}
        >
          <Icon className="w-3.5 h-3.5 text-green-600" />
        </span>
      )}
      {label}
    </label>
    {children}
    <AnimatePresence>
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          className="text-xs text-red-500 font-medium pl-1"
        >
          {error.message}
        </motion.p>
      )}
    </AnimatePresence>
  </div>
);

const inputCls =
  'w-full px-4 py-3 bg-white/80 border border-green-200 rounded-xl text-sm text-stone-800 placeholder-stone-400 outline-none transition-all focus:ring-2 focus:ring-green-400/40 focus:border-green-400';

const selectCls =
  'w-full px-4 py-3 bg-white/80 border border-green-200 rounded-xl text-sm text-stone-800 outline-none transition-all focus:ring-2 focus:ring-green-400/40 focus:border-green-400 appearance-none';

/* ── Main component ──────────────────────────────────── */
const AddFieldForm = ({ onSubmit, onCancel }) => {
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [location, setLocation] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm();

  const handleGetLocation = async () => {
    setIsGettingLocation(true);
    try {
      setTimeout(() => {
        const mockLocation = {
          lat: 28.6139,
          lng: 77.209,
          village: 'Narela',
          district: 'Delhi',
          state: 'Delhi',
        };
        setLocation(mockLocation);
        setValue('location', mockLocation);
        setIsGettingLocation(false);
      }, 2000);
    } catch {
      setIsGettingLocation(false);
    }
  };

  const onFormSubmit = (data) => {
    onSubmit({
      ...data,
      location: location || { village: data.village, district: '', state: '' },
    });
  };

  return (
    <div className="relative overflow-hidden rounded-2xl" style={{ background: '#f0fdf4' }}>
      {/* ── Header strip ─────────────────────────────── */}
      <div
        className="px-6 py-5"
        style={{
          background: 'linear-gradient(135deg, #16a34a 0%, #15803d 60%, #166534 100%)',
        }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(255,255,255,0.18)' }}
            >
              <Plus className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-white font-bold text-lg leading-tight">Add New Field</h2>
              <p className="text-green-200/80 text-xs mt-0.5">Enter your field details below</p>
            </div>
          </div>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="p-1.5 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* ── Form body ────────────────────────────────── */}
      <form onSubmit={handleSubmit(onFormSubmit)} className="p-5 space-y-5">
        {/* Field Name */}
        <InputGroup icon={Sprout} label="Field Name" error={errors.name}>
          <input
            type="text"
            {...register('name', { required: 'Field name is required' })}
            className={inputCls}
            placeholder="e.g. North Field, Main Khet"
          />
        </InputGroup>

        {/* Crop Type */}
        <InputGroup icon={Sprout} label="Crop Type" error={errors.crop}>
          <div className="relative">
            <select
              {...register('crop', { required: 'Crop type is required' })}
              className={selectCls}
            >
              <option value="">Select crop</option>
              {CROP_TYPES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            {/* Chevron */}
            <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-stone-400">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="m6 9 6 6 6-6" />
              </svg>
            </div>
          </div>
        </InputGroup>

        {/* Field Size — two-column */}
        <InputGroup icon={Ruler} label="Field Size" error={errors.area}>
          <div className="flex gap-2">
            <input
              type="number"
              step="0.1"
              {...register('area', {
                required: 'Area is required',
                min: { value: 0.1, message: 'Must be > 0' },
              })}
              className={`${inputCls} flex-1`}
              placeholder="Enter area"
            />
            <div className="relative w-28 flex-shrink-0">
              <select {...register('areaUnit')} className={selectCls}>
                <option value="acres">Acres</option>
                <option value="hectares">Hectares</option>
              </select>
              <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-stone-400">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </div>
            </div>
          </div>
        </InputGroup>

        {/* Soil Type */}
        <InputGroup icon={Layers} label="Soil Type" error={errors.soilType}>
          <div className="relative">
            <select
              {...register('soilType', { required: 'Soil type is required' })}
              className={selectCls}
            >
              <option value="">Select soil type</option>
              {SOIL_TYPES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-stone-400">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="m6 9 6 6 6-6" />
              </svg>
            </div>
          </div>
        </InputGroup>

        {/* Location */}
        <InputGroup icon={Navigation} label="Location">
          <div className="space-y-2">
            {/* GPS button */}
            <button
              type="button"
              onClick={handleGetLocation}
              disabled={isGettingLocation}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all active:scale-[0.98]"
              style={{
                background: isGettingLocation
                  ? '#d1fae5'
                  : 'linear-gradient(135deg, #16a34a, #15803d)',
                color: isGettingLocation ? '#16a34a' : '#ffffff',
                border: isGettingLocation ? '1px solid #a7f3d0' : 'none',
                boxShadow: isGettingLocation ? 'none' : '0 2px 8px rgba(22,163,74,0.3)',
              }}
            >
              {isGettingLocation ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Fetching location…
                </>
              ) : (
                <>
                  <MapPin className="w-4 h-4" />
                  Use GPS Location
                </>
              )}
            </button>

            {/* Location result */}
            <AnimatePresence>
              {location && (
                <motion.div
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2 p-3 rounded-xl"
                  style={{ background: '#dcfce7', border: '1px solid #bbf7d0' }}
                >
                  <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                  <span className="text-sm text-green-800 font-medium">
                    📍 {location.village}, {location.district}, {location.state}
                  </span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Manual fallback */}
            <input
              type="text"
              {...register('village')}
              className={inputCls}
              placeholder="Or enter village name manually"
            />
          </div>
        </InputGroup>

        {/* ── Action buttons ─────────────────────────── */}
        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 py-3 rounded-xl text-sm font-semibold transition-all active:scale-[0.98]"
            style={{
              background: '#ffffff',
              color: '#16a34a',
              border: '1px solid #bbf7d0',
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold text-white transition-all active:scale-[0.98]"
            style={{
              background: 'linear-gradient(135deg, #16a34a, #15803d)',
              boxShadow: '0 2px 8px rgba(22,163,74,0.3)',
            }}
          >
            <Plus className="w-4 h-4" />
            Add Field
          </button>
        </div>
      </form>
    </div>
  );
};

export { AddFieldForm };
