import React, { useState, useEffect, useRef } from 'react';
import { MapPin, Navigation, Map as MapIcon } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { useGeolocation } from '../../../hooks/useGeolocation.jsx';

const FieldMap = ({ field, onLocationUpdate }) => {
  const { location: currentLocation, error, getLocation } = useGeolocation();
  const [selectedCoords, setSelectedCoords] = useState(null);
  const mapRef = useRef(null);
  const [map, setMap] = useState(null);
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  useEffect(() => {
    if (window.google && mapRef.current && !map) {
      const fieldCenter = field?.location?.lat && field?.location?.lng 
        ? { lat: field.location.lat, lng: field.location.lng }
        : { lat: 28.6139, lng: 77.2090 }; // Default to Delhi

      const googleMap = new window.google.maps.Map(mapRef.current, {
        center: fieldCenter,
        zoom: 15,
        mapTypeId: 'satellite',
        disableDefaultUI: true,
        zoomControl: true,
      });

      // Field Marker
      if (field?.location?.lat && field?.location?.lng) {
        new window.google.maps.Marker({
          position: fieldCenter,
          map: googleMap,
          title: field.name,
          icon: {
            path: window.google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
            scale: 5,
            fillColor: '#16a34a',
            fillOpacity: 1,
            strokeWeight: 2,
            strokeColor: '#fff',
          }
        });
      }

      setMap(googleMap);
      setIsMapLoaded(true);
    }
  }, [field, map]);

  useEffect(() => {
    if (map && selectedCoords) {
      const userPos = { lat: selectedCoords.latitude, lng: selectedCoords.longitude };
      
      new window.google.maps.Marker({
        position: userPos,
        map: map,
        title: 'You',
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 7,
          fillColor: '#dc2626',
          fillOpacity: 1,
          strokeWeight: 2,
          strokeColor: '#fff',
        }
      });

      map.panTo(userPos);
    }
  }, [map, selectedCoords]);

  const handleEnableGPS = async () => {
    const coords = await getLocation();
    if (coords) {
      setSelectedCoords(coords);
      onLocationUpdate?.(coords);
    }
  };

  return (
    <Card className="p-0 overflow-hidden border-none shadow-none theme-bg-primary">
      <div className="flex items-center justify-between p-4 theme-bg-secondary">
        <div className="flex items-center gap-2">
          <MapIcon className="w-5 h-5 theme-text-accent-primary" />
          <h3 className="text-lg font-bold theme-text-primary">Live Field Map</h3>
        </div>
        <Button
          variant={currentLocation ? "success" : "outline"}
          size="sm"
          icon={Navigation}
          onClick={handleEnableGPS}
          disabled={!!currentLocation}
        >
          {currentLocation ? 'GPS Online' : 'Locate Me'}
        </Button>
      </div>

      <div className="flex flex-col">
        {/* Map Container */}
        <div 
          ref={mapRef} 
          className="w-full h-80 theme-bg-secondary"
          style={{ minHeight: '320px' }}
        >
          {!isMapLoaded && (
            <div className="w-full h-full flex items-center justify-center theme-text-secondary italic">
              Loading satellite imagery...
            </div>
          )}
        </div>

        {/* Info Panel */}
        <div className="p-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {field?.location && (
              <div className="p-4 theme-bg-secondary rounded-2xl border theme-border">
                <div className="flex items-center gap-2 mb-2">
                  <MapPin className="w-4 h-4 theme-text-accent-primary" />
                  <span className="text-sm font-bold theme-text-primary">Field Location</span>
                </div>
                <div className="text-xs theme-text-secondary leading-relaxed">
                  <p className="font-semibold theme-text-primary">{field.name}</p>
                  <p>{field.location.village}, {field.location.district || ''}</p>
                  <p>{field.location.state}</p>
                </div>
              </div>
            )}

            {selectedCoords && (
              <div className="p-4 bg-theme-accent-primary/5 rounded-2xl border border-theme-accent-primary/20">
                <div className="flex items-center gap-2 mb-2">
                  <Navigation className="w-4 h-4 theme-text-accent-primary" />
                  <span className="text-sm font-bold theme-text-accent-primary">Your Device Location</span>
                </div>
                <div className="text-xs theme-text-secondary">
                  <p>Lat: {selectedCoords.latitude.toFixed(6)}</p>
                  <p>Lng: {selectedCoords.longitude.toFixed(6)}</p>
                  <p className="mt-1 opacity-70">Accuracy: ±{selectedCoords.accuracy.toFixed(1)}m</p>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="p-3 theme-bg-danger/10 border border-theme-danger/20 rounded-xl">
              <p className="text-xs theme-text-danger font-medium">{error}</p>
            </div>
          )}

          {/* Field Details Grid */}
          {field && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Area', value: `${field.area} ${field.areaUnit}`, icon: '📐' },
                { label: 'Soil', value: field.soilType, icon: '🪨' },
                { label: 'Crop', value: field.crop, icon: '🌾' },
                { label: 'Stage', value: field.growthStage, icon: '🌱' },
              ].map(item => (
                <div key={item.label} className="p-3 theme-bg-secondary rounded-xl border theme-border">
                  <div className="text-[10px] theme-text-secondary uppercase tracking-wider mb-1">
                    {item.icon} {item.label}
                  </div>
                  <div className="text-sm font-bold theme-text-primary truncate">
                    {item.value}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

export { FieldMap };
