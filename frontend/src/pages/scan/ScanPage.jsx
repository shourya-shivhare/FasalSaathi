import React, { useState, useRef } from 'react';
import { Camera, ScanLine, AlertCircle, CheckCircle2, History, ArrowRight, X } from 'lucide-react';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { TopBar } from '../../components/layout/TopBar';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';

const ScanPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const fileInputRef = useRef(null);

  const mockHistory = [
    { id: 1, name: 'Aphids', date: '24 Mar', confidence: 92, image: 'https://images.unsplash.com/photo-1628350565513-318a7201f720?auto=format&fit=crop&q=80&w=100' },
    { id: 2, name: 'Leaf Blight', date: '20 Mar', confidence: 88, image: 'https://images.unsplash.com/photo-1599420186946-7b6fb4e297f0?auto=format&fit=crop&q=80&w=100' },
    { id: 3, name: 'Spotted Beetle', date: '15 Mar', confidence: 95, image: 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&q=80&w=100' },
  ];

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result);
        setIsScanning(true);
        // Simulate scanning delay
        setTimeout(() => setIsScanning(false), 2000);
      };
      reader.readAsDataURL(file);
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
    setIsScanning(false);
  };

  return (
    <PageWrapper>
      <TopBar
        icon={ScanLine}
        title="Pest Scanner"
        subtitle="AI-powered crop health detection"
      />

      <div className="p-4 space-y-6 pb-24">
        {/* Upload Zone */}
        {!selectedImage ? (
          <Card 
            className="flex flex-col items-center justify-center py-12 border-2 border-dashed theme-border cursor-pointer hover:theme-bg-secondary transition-all active:scale-[0.98]"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="w-16 h-16 rounded-full theme-bg-surface-hover flex items-center justify-center mb-4">
              <Camera className="w-8 h-8 theme-text-accent-primary" />
            </div>
            <p className="text-lg font-bold theme-text-primary">Apni fasal ki photo lo</p>
            <p className="text-sm theme-text-secondary mt-1">Tap to capture or upload</p>
            <input 
              type="file" 
              ref={fileInputRef}
              onChange={handleImageSelect}
              accept="image/*"
              className="hidden"
            />
          </Card>
        ) : (
          <div className="relative rounded-2xl overflow-hidden shadow-lg border theme-border">
            <img src={selectedImage} alt="Crop preview" className="w-full aspect-square object-cover" />
            <button 
              onClick={clearImage}
              className="absolute top-3 right-3 p-2 rounded-full bg-black/40 text-white backdrop-blur-md hover:bg-black/60 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            {isScanning && (
              <div className="absolute inset-0 bg-black/20 backdrop-blur-[2px] flex flex-col items-center justify-center">
                <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin mb-3" />
                <p className="text-white font-bold drop-shadow-md">Scanning...</p>
              </div>
            )}
          </div>
        )}

        {/* Result Card */}
        {(selectedImage || isScanning) && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <Card className="overflow-hidden border-l-4 border-l-theme-accent-primary">
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  {selectedImage && (
                    <div className="w-16 h-16 rounded-lg overflow-hidden border theme-border flex-shrink-0">
                      <img src={selectedImage} alt="Thumbnail" className="w-full h-full object-cover" />
                    </div>
                  )}
                  <div>
                    <h3 className="font-bold text-lg theme-text-primary">
                      {isScanning ? 'Detecting...' : 'Aphids (Tentative)'}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant={isScanning ? 'neutral' : 'warning'}>
                        {isScanning ? 'Calculating...' : '87% Confidence'}
                      </Badge>
                    </div>
                  </div>
                </div>
                {!isScanning && <CheckCircle2 className="w-6 h-6 theme-text-success" />}
              </div>
            </Card>

            {/* Treatment Panel */}
            <Card className="theme-bg-secondary border theme-border">
              <h4 className="font-bold theme-text-primary mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 theme-text-warning" />
                Treatment Plan
              </h4>
              <div className="grid grid-cols-1 gap-4">
                <div className="space-y-1">
                  <p className="text-xs font-semibold uppercase tracking-wider theme-text-secondary">Recommended Treatment</p>
                  <p className="theme-text-primary font-medium">{isScanning ? '—' : 'Neem Oil Spray (3%)'}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-xs font-semibold uppercase tracking-wider theme-text-secondary">Dosage</p>
                    <p className="theme-text-primary font-medium">{isScanning ? '—' : '200ml per acre'}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs font-semibold uppercase tracking-wider theme-text-secondary">Urgency</p>
                    <p className={`${isScanning ? 'theme-text-primary' : 'theme-text-warning'} font-medium`}>
                      {isScanning ? '—' : 'Medium'}
                    </p>
                  </div>
                </div>
              </div>
              {!isScanning && (
                <Button variant="primary" size="sm" className="mt-6" fullWidth icon={ArrowRight}>
                  View Detailed Guide
                </Button>
              )}
            </Card>
          </div>
        )}

        {/* History Strip */}
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <h3 className="font-bold theme-text-primary flex items-center gap-2">
              <History className="w-5 h-5 theme-text-accent-primary" />
              Recent Scans
            </h3>
            <button className="text-sm font-medium theme-text-accent-primary">See All</button>
          </div>
          <div className="flex gap-4 overflow-x-auto pb-4 -mx-1 px-1 scrollbar-hide">
            {mockHistory.map((scan) => (
              <div 
                key={scan.id}
                className="flex-shrink-0 w-32 backdrop-blur-md theme-bg-secondary p-3 rounded-2xl border theme-border transition-all active:scale-95"
              >
                <div className="w-full aspect-square rounded-xl overflow-hidden mb-2">
                  <img src={scan.image} alt={scan.name} className="w-full h-full object-cover" />
                </div>
                <p className="text-xs font-bold theme-text-primary truncate">{scan.name}</p>
                <p className="text-[10px] theme-text-secondary mt-0.5">{scan.date}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageWrapper>
  );
};

export default ScanPage;
