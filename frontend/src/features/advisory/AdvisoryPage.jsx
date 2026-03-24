import React from 'react';
import { BookOpen } from 'lucide-react';
import { TopBar } from '../../components/layout/TopBar';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { CropCalendar } from './components/CropCalendar';
import { PestAlertCard } from './components/PestAlertCard';
import { SchemeCard } from './components/SchemeCard';
import { useFieldStore } from '../../stores/useFieldStore.jsx';
import { mockPestAlerts, mockSchemes } from '../../lib/mockData.jsx';

const AdvisoryPage = () => {
  const { getActiveField } = useFieldStore();
  const activeField = getActiveField();

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
        <div>
          <h2 className="text-lg font-semibold text-green-800 mb-3">🐛 Pest Alerts</h2>
          <div className="space-y-4">
            {relevantPestAlerts.map((alert) => (
              <PestAlertCard key={alert.id} pestAlert={alert} />
            ))}
          </div>
        </div>

        {/* Government Schemes */}
        <div>
          <h2 className="text-lg font-semibold text-green-800 mb-3">📜 Government Schemes</h2>
          <div className="space-y-4">
            {featuredSchemes.map((scheme) => (
              <SchemeCard key={scheme.id} scheme={scheme} />
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
            <h3 className="text-lg font-semibold text-stone-900 mb-2">
              Set up your field for personalized advice
            </h3>
            <p className="text-stone-600 mb-4">
              Add field details to get crop-specific guidance and recommendations
            </p>
          </div>
        )}
      </div>
    </PageWrapper>
  );
};

export { AdvisoryPage };
