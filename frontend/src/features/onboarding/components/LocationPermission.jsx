import React, { useState } from 'react';
import { MapPin, Navigation, Loader2 } from 'lucide-react';
import { Button } from '../../../components/ui/Button';

const LocationPermission = ({ onLocationSet, onNext, onBack }) => {
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [location, setLocation] = useState(null);
  const [pincode, setPincode] = useState('');
  const [useManualEntry, setUseManualEntry] = useState(false);

  const handleGetLocation = async () => {
    setIsGettingLocation(true);
    
    try {
      // Simulate geolocation API
      setTimeout(() => {
        const mockLocation = {
          lat: 28.6139,
          lng: 77.2090,
          village: 'Narela',
          district: 'Delhi',
          state: 'Delhi',
          pincode: '110040',
        };
        setLocation(mockLocation);
        setIsGettingLocation(false);
      }, 2000);
    } catch (error) {
      console.error('Error getting location:', error);
      setIsGettingLocation(false);
    }
  };

  const handlePincodeSubmit = () => {
    if (pincode.length === 6) {
      // Mock location lookup by pincode
      const mockLocation = {
        pincode: pincode,
        village: 'Demo Village',
        district: 'Demo District',
        state: 'Demo State',
      };
      setLocation(mockLocation);
    }
  };

  const handleContinue = () => {
    if (location) {
      onLocationSet(location);
      onNext();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 bg-stone-50">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="text-6xl mb-4">📍</div>
          <h1 className="text-2xl font-bold text-stone-900 mb-2">
            Tell us your location
          </h1>
          <p className="text-stone-600">
            We'll use this to provide weather alerts and local market prices
          </p>
        </div>

        {!useManualEntry ? (
          /* GPS Location Option */
          <div className="space-y-4">
            <Button
              variant="primary"
              size="lg"
              fullWidth
              onClick={handleGetLocation}
              disabled={isGettingLocation}
              icon={isGettingLocation ? Loader2 : Navigation}
              className="h-16"
            >
              {isGettingLocation ? 'Getting Location...' : 'Use GPS Location'}
            </Button>

            <div className="text-center">
              <button
                onClick={() => setUseManualEntry(true)}
                className="text-stone-500 hover:text-stone-700 text-sm underline"
              >
                Or enter pincode manually
              </button>
            </div>

            {location && !useManualEntry && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <MapPin className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-green-900">Location detected</span>
                </div>
                <div className="text-sm text-green-800">
                  <p>{location.village}, {location.district}</p>
                  <p>{location.state} - {location.pincode}</p>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* Manual Pincode Entry */
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Enter your pincode
              </label>
              <input
                type="text"
                value={pincode}
                onChange={(e) => setPincode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="6-digit pincode"
                className="w-full px-4 py-3 bg-white border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-center text-lg"
                maxLength={6}
              />
            </div>

            <Button
              variant="primary"
              size="lg"
              fullWidth
              onClick={handlePincodeSubmit}
              disabled={pincode.length !== 6}
              className="h-16"
            >
              Verify Pincode
            </Button>

            <div className="text-center">
              <button
                onClick={() => setUseManualEntry(false)}
                className="text-stone-500 hover:text-stone-700 text-sm underline"
              >
                ← Back to GPS option
              </button>
            </div>

            {location && useManualEntry && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <MapPin className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-green-900">Location found</span>
                </div>
                <div className="text-sm text-green-800">
                  <p>{location.village}, {location.district}</p>
                  <p>{location.state}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Progress Indicator */}
        <div className="flex justify-center gap-2">
          <div className="w-8 h-2 bg-stone-300 rounded-full" />
          <div className="w-8 h-2 bg-brand-600 rounded-full" />
          <div className="w-8 h-2 bg-stone-300 rounded-full" />
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
            onClick={handleContinue}
            disabled={!location}
            className="flex-1"
          >
            Continue
          </Button>
        </div>
      </div>
    </div>
  );
};

export { LocationPermission };
