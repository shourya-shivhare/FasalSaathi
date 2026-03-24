import React from 'react';
import { LayoutDashboard } from 'lucide-react';
import { TopBar } from '../../components/layout/TopBar';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { SyncStatus } from '../../components/shared/SyncStatus';
import { WeatherCard } from './components/WeatherCard';
import { SoilHealthGrid } from './components/SoilHealthGrid';
import { CropStatusBanner } from './components/CropStatusBanner';
import { IrrigationTimer } from './components/IrrigationTimer';
import { AlertsFeed } from './components/AlertsFeed';
import { useFieldData } from './hooks/useFieldData';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { mockAlerts } from '../../lib/mockData.jsx';

const DashboardPage = () => {
  const { farmer } = useUserStore();
  const {
    activeField,
    weather,
    soil,
    irrigation,
    hasFields,
    isLoading,
  } = useFieldData();

  if (isLoading) {
    return (
      <PageWrapper>
        <div className="pt-14 p-4 space-y-4">
          <div className="animate-pulse space-y-4">
            <div className="h-24 bg-stone-200 rounded-lg" />
            <div className="grid grid-cols-2 gap-3">
              <div className="h-32 bg-stone-200 rounded-lg" />
              <div className="h-32 bg-stone-200 rounded-lg" />
            </div>
            <div className="h-40 bg-stone-200 rounded-lg" />
            <div className="h-48 bg-stone-200 rounded-lg" />
            <div className="h-32 bg-stone-200 rounded-lg" />
          </div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <TopBar
        icon={LayoutDashboard}
        title={hasFields ? activeField?.name || 'My Farm' : 'My Farm'}
        subtitle={farmer.village}
        rightAction={<SyncStatus isOnline={true} lastSync={new Date()} />}
      />

      <div className="p-4 space-y-4 max-w-7xl mx-auto">
        {/* Weather Card */}
        <WeatherCard weather={weather} />

        {/* Soil Health Grid */}
        <div>
          <h2 className="text-lg font-semibold text-green-800 mb-3">
            🌱 Soil Health
          </h2>
          <SoilHealthGrid soil={soil} />
        </div>

        {/* Crop Status Banner */}
        {hasFields && activeField && (
          <CropStatusBanner field={activeField} />
        )}

        {/* Irrigation Timer */}
        <IrrigationTimer irrigation={irrigation} />

        {/* Alerts Feed */}
        <AlertsFeed alerts={mockAlerts} />

        {/* Empty State for No Fields */}
        {!hasFields && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🌱</div>
            <h3 className="text-lg font-semibold text-stone-900 mb-2">
              No fields added yet
            </h3>
            <p className="text-stone-600 mb-4">
              Add your first field to start tracking your farm
            </p>
          </div>
        )}
      </div>
    </PageWrapper>
  );
};

export { DashboardPage };
