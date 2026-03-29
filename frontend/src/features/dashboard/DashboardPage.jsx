import React from 'react';
import { LayoutDashboard, Camera, ScanLine } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '../../components/layout/TopBar';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
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
  const navigate = useNavigate();
  const { farmer, resetOnboarding } = useUserStore();
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
        <div className="pt-14 p-4 space-y-4 theme-bg-primary min-h-screen">
          <div className="animate-pulse space-y-4">
            <div className="h-24 theme-bg-surface-hover rounded-lg" />
            <div className="grid grid-cols-2 gap-3">
              <div className="h-32 theme-bg-surface-hover rounded-lg" />
              <div className="h-32 theme-bg-surface-hover rounded-lg" />
            </div>
            <div className="h-40 theme-bg-surface-hover rounded-lg" />
            <div className="h-48 theme-bg-surface-hover rounded-lg" />
            <div className="h-32 theme-bg-surface-hover rounded-lg" />
          </div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper className="min-h-screen">
      <TopBar
        icon={LayoutDashboard}
        title={hasFields ? activeField?.name || 'My Farm' : 'My Farm'}
        subtitle={farmer.village}
        rightAction={<SyncStatus isOnline={true} lastSync={new Date()} />}
      />

      <div className="p-4 space-y-4 max-w-7xl mx-auto">
        {/* Weather Card */}
        <WeatherCard weather={weather} />

        {/* Pest Detection Card */}
        <Card 
          className="flex items-center justify-between p-4 cursor-pointer hover:theme-bg-secondary transition-all active:scale-[0.98] border-l-4 border-l-theme-accent-primary"
          onClick={() => navigate('/scan')}
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl theme-bg-surface-hover flex items-center justify-center">
              <Camera className="w-6 h-6 theme-text-accent-primary" />
            </div>
            <div>
              <h3 className="font-bold theme-text-primary">Pest Detection</h3>
              <p className="text-sm theme-text-secondary">Apni fasal scan karo</p>
            </div>
          </div>
          <Button variant="outline" size="sm" icon={ScanLine}>
            Scan Now
          </Button>
        </Card>

        {/* Soil Health Grid */}
        <div>
          <h2 className="text-lg font-semibold theme-text-success mb-3 flex items-center gap-2">
            <span>🌱</span> Soil Health
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
          <div className="text-center py-12 rounded-xl border theme-border theme-bg-secondary transition-all duration-200">
            <div className="text-6xl mb-4">🌱</div>
            <h3 className="text-lg font-semibold theme-text-primary mb-2">
              No fields added yet
            </h3>
            <p className="theme-text-secondary mb-4">
              Add your first field to start tracking your farm
            </p>
          </div>
        )}

        {/* Dev Reset Button */}
        {import.meta.env.DEV && (
          <div className="flex justify-center mt-8 pb-8">
            <button
              onClick={() => {
                resetOnboarding();
                window.location.href = '/';
              }}
              className="px-4 py-2 bg-red-600/80 text-white font-medium rounded-lg opacity-50 hover:opacity-100 transition-opacity flex items-center gap-2 text-sm"
            >
              Reset Testing State (Dev Only)
            </button>
          </div>
        )}
      </div>
    </PageWrapper>
  );
};

export { DashboardPage };