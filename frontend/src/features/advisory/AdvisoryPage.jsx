import React, { useState } from 'react';
import { BookOpen, Camera, ScanLine, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { TopBar } from '../../components/layout/TopBar';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { CropCalendar } from './components/CropCalendar';
import { PestAlertCard } from './components/PestAlertCard';
import { SchemeCard } from './components/SchemeCard';
import { useFieldStore } from '../../stores/useFieldStore.jsx';
import { mockPestAlerts, mockSchemes } from '../../lib/mockData.jsx';

const AdvisoryPage = () => {
  const navigate = useNavigate();
  const { getActiveField } = useFieldStore();
  const activeField = getActiveField();
  const [expandedSchemeId, setExpandedSchemeId] = useState(null);

  const toggleScheme = (id) => {
    setExpandedSchemeId(prev => prev === id ? null : id);
  };

  // Filter pest alerts for the current crop and region
  const relevantPestAlerts = mockPestAlerts.filter(alert => 
    !activeField || alert.affectedCrop === activeField.crop
  );

  // Show top 3 schemes
  const featuredSchemes = mockSchemes.slice(0, 3);

  return (
    <PageWrapper>
      <TopBar
        icon={BookOpen}
        title="Advisory"
        subtitle={activeField ? `${activeField.crop} guidance` : 'Farming guidance & schemes'}
      />

      <div className="p-4 space-y-4">
        {/* Crop Calendar */}
        {activeField && (
          <CropCalendar
            crop={activeField.crop}
            growthStage={activeField.growthStage}
            plantingDate={new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)} // 30 days ago
          />
        )}

        {/* Pest Alerts */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold theme-text-primary flex items-center gap-2">
              <span className="text-xl">🐛</span> Pest Alerts
            </h2>
          </div>

          {/* Pest Scanner Banner */}
          <Card 
            className="relative overflow-hidden p-6 bg-gradient-to-br from-theme-bg-secondary to-theme-accent-primary/5 border theme-border"
          >
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 relative z-10">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl theme-bg-surface flex items-center justify-center shadow-sm border theme-border">
                  <ScanLine className="w-8 h-8 theme-text-accent-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-bold theme-text-primary">Fasal mein keede?</h3>
                  <p className="theme-text-secondary text-sm">Apni fasal scan karein aur upchar payein</p>
                </div>
              </div>
              <Button 
                variant="primary" 
                size="md" 
                onClick={() => navigate('/scan')}
                className="w-full sm:w-auto shadow-md"
                icon={ArrowRight}
              >
                Scan Now
              </Button>
            </div>
            {/* Decorative Background Icons */}
            <Camera className="absolute -right-4 -bottom-4 w-24 h-24 theme-text-accent-primary opacity-[0.03] pointer-events-none rotate-12" />
          </Card>

          <div className="space-y-4">
            {relevantPestAlerts.map((alert) => (
              <PestAlertCard key={alert.id} pestAlert={alert} />
            ))}
          </div>
        </div>

        {/* Government Schemes */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold theme-text-primary flex items-center gap-2">
            <span className="text-xl">📜</span> Government Schemes
          </h2>
          <div className="space-y-4">
            {featuredSchemes.map((scheme) => (
              <SchemeCard 
                key={scheme.id} 
                scheme={scheme} 
                isExpanded={expandedSchemeId === scheme.id}
                onToggle={() => toggleScheme(scheme.id)}
              />
            ))}
          </div>
        </div>

        {/* Weather Advisory */}
        <div className="info-banner">
          <h3 className="font-semibold text-green-800 mb-2 flex items-center gap-2">
            🌦️ Weather Advisory
          </h3>
          <div className="text-sm text-green-700 space-y-1">
            <p>• High temperature expected in the next 48 hours</p>
            <p>• Consider afternoon irrigation to protect crops</p>
            <p>• Monitor for heat stress in young plants</p>
            <p>• Avoid fertilizer application during peak heat hours</p>
          </div>
        </div>

        {/* Empty State */}
        {!activeField && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📋</div>
            <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>
              Set up your field for personalized advice
            </h3>
            <p className="mb-4" style={{ color: 'var(--color-text-secondary)' }}>
              Add field details to get crop-specific guidance and recommendations
            </p>
          </div>
        )}
      </div>
    </PageWrapper>
  );
};

export { AdvisoryPage };
