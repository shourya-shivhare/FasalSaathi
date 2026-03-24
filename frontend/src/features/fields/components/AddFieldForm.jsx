import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { MapPin, Plus } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { CROP_TYPES, SOIL_TYPES } from '../../../lib/constants.jsx';

const AddFieldForm = ({ onSubmit, onCancel }) => {
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [location, setLocation] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm();

  const areaUnit = watch('areaUnit', 'acres');

  const handleGetLocation = async () => {
    setIsGettingLocation(true);
    
    try {
      // Simulate geolocation
      setTimeout(() => {
        const mockLocation = {
          lat: 28.6139,
          lng: 77.2090,
          village: 'Narela',
          district: 'Delhi',
          state: 'Delhi',
        };
        setLocation(mockLocation);
        setValue('location', mockLocation);
        setIsGettingLocation(false);
      }, 2000);
    } catch (error) {
      console.error('Error getting location:', error);
      setIsGettingLocation(false);
    }
  };

  const onFormSubmit = (data) => {
    const fieldData = {
      ...data,
      location: location || { village: data.village, district: '', state: '' },
    };
    onSubmit(fieldData);
  };

  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold text-stone-900 mb-6">Add New Field</h2>
      
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-stone-700 mb-2">
            Field Name
          </label>
          <input
            type="text"
            {...register('name', { required: 'Field name is required' })}
            className="w-full px-4 py-3 bg-stone-50 border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            placeholder="e.g., North Field, Main Field"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-stone-700 mb-2">
            Crop Type
          </label>
          <select
            {...register('crop', { required: 'Crop type is required' })}
            className="w-full px-4 py-3 bg-stone-50 border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
          >
            <option value="">Select crop</option>
            {CROP_TYPES.map((crop) => (
              <option key={crop} value={crop}>
                {crop}
              </option>
            ))}
          </select>
          {errors.crop && (
            <p className="mt-1 text-sm text-red-600">{errors.crop.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-stone-700 mb-2">
            Field Size
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              step="0.1"
              {...register('area', { 
                required: 'Area is required',
                min: { value: 0.1, message: 'Area must be greater than 0' }
              })}
              className="flex-1 px-4 py-3 bg-stone-50 border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              placeholder="Enter area"
            />
            <select
              {...register('areaUnit')}
              className="px-4 py-3 bg-stone-50 border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            >
              <option value="acres">Acres</option>
              <option value="hectares">Hectares</option>
            </select>
          </div>
          {errors.area && (
            <p className="mt-1 text-sm text-red-600">{errors.area.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-stone-700 mb-2">
            Soil Type
          </label>
          <select
            {...register('soilType', { required: 'Soil type is required' })}
            className="w-full px-4 py-3 bg-stone-50 border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
          >
            <option value="">Select soil type</option>
            {SOIL_TYPES.map((soil) => (
              <option key={soil} value={soil}>
                {soil}
              </option>
            ))}
          </select>
          {errors.soilType && (
            <p className="mt-1 text-sm text-red-600">{errors.soilType.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-stone-700 mb-2">
            Location
          </label>
          <div className="space-y-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleGetLocation}
              disabled={isGettingLocation}
              icon={MapPin}
              fullWidth
            >
              {isGettingLocation ? 'Getting Location...' : 'Use GPS Location'}
            </Button>
            
            {location && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  📍 {location.village}, {location.district}, {location.state}
                </p>
              </div>
            )}
            
            <input
              type="text"
              {...register('village')}
              className="w-full px-4 py-3 bg-stone-50 border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              placeholder="Or enter village name manually"
            />
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            icon={Plus}
            className="flex-1"
          >
            Add Field
          </Button>
        </div>
      </form>
    </Card>
  );
};

export { AddFieldForm };
