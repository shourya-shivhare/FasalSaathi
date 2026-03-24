import React, { useState } from 'react';
import { Wheat, Sprout, Flower2, TreePine, Plus } from 'lucide-react';
import { Button } from '../../../components/ui/Button';
import { CROP_TYPES } from '../../../lib/constants.jsx';

const CropSetup = ({ onCropSetup, onNext, onBack }) => {
  const [selectedCrops, setSelectedCrops] = useState([]);
  const [fieldSize, setFieldSize] = useState('');
  const [areaUnit, setAreaUnit] = useState('acres');

  const getCropIcon = (crop) => {
    const cropIcons = {
      Wheat: Wheat,
      Rice: Sprout,
      Cotton: Flower2,
      Soybean: TreePine,
      Maize: Sprout,
    };
    const Icon = cropIcons[crop] || Sprout;
    return <Icon className="w-8 h-8" />;
  };

  const toggleCrop = (crop) => {
    setSelectedCrops(prev => 
      prev.includes(crop) 
        ? prev.filter(c => c !== crop)
        : [...prev, crop]
    );
  };

  const handleSubmit = () => {
    if (selectedCrops.length > 0 && fieldSize) {
      onCropSetup({
        crops: selectedCrops,
        fieldSize: parseFloat(fieldSize),
        areaUnit,
      });
      onNext();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 bg-stone-50">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="text-6xl mb-4">🌱</div>
          <h1 className="text-2xl font-bold text-stone-900 mb-2">
            What do you grow?
          </h1>
          <p className="text-stone-600">
            Select the crops you grow and your field size
          </p>
        </div>

        {/* Crop Selection */}
        <div>
          <label className="block text-sm font-medium text-stone-700 mb-3">
            Select your crops (you can choose multiple)
          </label>
          <div className="grid grid-cols-2 gap-3">
            {CROP_TYPES.map((crop) => (
              <button
                key={crop}
                onClick={() => toggleCrop(crop)}
                className={`p-4 rounded-xl border-2 transition-all ${
                  selectedCrops.includes(crop)
                    ? 'border-brand-500 bg-brand-50 text-brand-700'
                    : 'border-stone-200 bg-white text-stone-700 hover:border-stone-300'
                }`}
              >
                <div className="flex flex-col items-center gap-2">
                  {getCropIcon(crop)}
                  <span className="text-sm font-medium">{crop}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Field Size */}
        <div>
          <label className="block text-sm font-medium text-stone-700 mb-2">
            Total field size
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              step="0.1"
              value={fieldSize}
              onChange={(e) => setFieldSize(e.target.value)}
              placeholder="Enter size"
              className="flex-1 px-4 py-3 bg-white border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            />
            <select
              value={areaUnit}
              onChange={(e) => setAreaUnit(e.target.value)}
              className="px-4 py-3 bg-white border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            >
              <option value="acres">Acres</option>
              <option value="hectares">Hectares</option>
            </select>
          </div>
        </div>

        {/* Summary */}
        {selectedCrops.length > 0 && fieldSize && (
          <div className="p-4 bg-stone-100 rounded-lg">
            <h3 className="font-medium text-stone-900 mb-2">Setup Summary</h3>
            <div className="text-sm text-stone-700 space-y-1">
              <p>• {selectedCrops.length} crop{selectedCrops.length > 1 ? 's' : ''} selected</p>
              <p>• Field size: {fieldSize} {areaUnit}</p>
              <p>• Location services enabled</p>
            </div>
          </div>
        )}

        {/* Progress Indicator */}
        <div className="flex justify-center gap-2">
          <div className="w-8 h-2 bg-stone-300 rounded-full" />
          <div className="w-8 h-2 bg-stone-300 rounded-full" />
          <div className="w-8 h-2 bg-brand-600 rounded-full" />
        </div>

        {/* Navigation */}
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={onBack}
            className="flex-1"
          >
            Back
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={selectedCrops.length === 0 || !fieldSize}
            icon={Plus}
            className="flex-1"
          >
            Start using FasalSaathi →
          </Button>
        </div>
      </div>
    </div>
  );
};

export { CropSetup };
