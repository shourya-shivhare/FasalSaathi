import React, { useState } from 'react';
import { MapPin, Navigation } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { useGeolocation } from '../../../hooks/useGeolocation.jsx';

const FieldMap = ({ field, onLocationUpdate }) => {
  const { location: currentLocation, error, getLocation } = useGeolocation();
  const [selectedCoords, setSelectedCoords] = useState(null);

  const handleEnableGPS = async () => {
    const coords = await getLocation();
    if (coords) {
      setSelectedCoords(coords);
      onLocationUpdate?.(coords);
    }
  };

  const FieldMapSVG = () => (
    <svg
      viewBox="0 0 400 300"
      className="w-full h-full"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Background */}
      <rect width="400" height="300" fill="#f5f5f4" />
      
      {/* Grid lines */}
      {[...Array(8)].map((_, i) => (
        <line
          key={`v-${i}`}
          x1={i * 50}
          y1="0"
          x2={i * 50}
          y2="300"
          stroke="#e7e5e4"
          strokeWidth="1"
        />
      ))}
      {[...Array(6)].map((_, i) => (
        <line
          key={`h-${i}`}
          x1="0"
          y1={i * 50}
          x2="400"
          y2={i * 50}
          stroke="#e7e5e4"
          strokeWidth="1"
        />
      ))}
      
      {/* Field boundary polygon */}
      <polygon
        points="100,80 320,100 300,220 120,200"
        fill="#22c55e"
        fillOpacity="0.3"
        stroke="#16a34a"
        strokeWidth="2"
      />
      
      {/* Field center marker */}
      <circle cx="210" cy="150" r="8" fill="#16a34a" />
      <circle cx="210" cy="150" r="4" fill="white" />
      
      {/* GPS location marker if available */}
      {selectedCoords && (
        <g>
          <circle cx="250" cy="120" r="6" fill="#dc2626" />
          <circle cx="250" cy="120" r="3" fill="white" />
          <text x="260" y="125" fontSize="12" fill="#dc2626">You</text>
        </g>
      )}
      
      {/* Scale */}
      <g transform="translate(20, 270)">
        <line x1="0" y1="0" x2="50" y2="0" stroke="#44403c" strokeWidth="2" />
        <line x1="0" y1="-3" x2="0" y2="3" stroke="#44403c" strokeWidth="2" />
        <line x1="50" y1="-3" x2="50" y2="3" stroke="#44403c" strokeWidth="2" />
        <text x="25" y="-5" fontSize="10" textAnchor="middle" fill="#44403c">100m</text>
      </g>
      
      {/* North arrow */}
      <g transform="translate(370, 30)">
        <line x1="0" y1="10" x2="0" y2="-10" stroke="#44403c" strokeWidth="2" />
        <polygon points="0,-15 -5,-10 5,-10" fill="#44403c" />
        <text x="0" y="-20" fontSize="12" textAnchor="middle" fill="#44403c">N</text>
      </g>
    </svg>
  );

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-stone-900">Field Map</h3>
        <Button
          variant="outline"
          size="sm"
          icon={Navigation}
          onClick={handleEnableGPS}
          disabled={!!currentLocation}
        >
          {currentLocation ? 'GPS Enabled' : 'Enable GPS'}
        </Button>
      </div>

      <div className="space-y-4">
        {/* Map SVG */}
        <div className="h-64 bg-stone-50 rounded-lg overflow-hidden">
          <FieldMapSVG />
        </div>

        {/* Location Information */}
        <div className="space-y-2">
          {field?.location && (
            <div className="p-3 bg-stone-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <MapPin className="w-4 h-4 text-stone-600" />
                <span className="text-sm font-medium text-stone-900">Field Location</span>
              </div>
              <div className="text-sm text-stone-600">
                <p>{field.location.village}, {field.location.district}</p>
                <p>{field.location.state}</p>
              </div>
            </div>
          )}

          {selectedCoords && (
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Navigation className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Your Location</span>
              </div>
              <div className="text-sm text-blue-700">
                <p>Latitude: {selectedCoords.latitude.toFixed(6)}</p>
                <p>Longitude: {selectedCoords.longitude.toFixed(6)}</p>
                <p>Accuracy: ±{selectedCoords.accuracy}m</p>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 rounded-lg">
              <div className="text-sm text-red-700">
                <p className="font-medium">Location Error</p>
                <p>{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Field Details */}
        {field && (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-stone-600">Area:</span>
              <span className="ml-2 font-medium text-stone-900">
                {field.area} {field.areaUnit}
              </span>
            </div>
            <div>
              <span className="text-stone-600">Soil Type:</span>
              <span className="ml-2 font-medium text-stone-900">
                {field.soilType}
              </span>
            </div>
            <div>
              <span className="text-stone-600">Crop:</span>
              <span className="ml-2 font-medium text-stone-900">
                {field.crop}
              </span>
            </div>
            <div>
              <span className="text-stone-600">Growth Stage:</span>
              <span className="ml-2 font-medium text-stone-900">
                {field.growthStage}
              </span>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export { FieldMap };
