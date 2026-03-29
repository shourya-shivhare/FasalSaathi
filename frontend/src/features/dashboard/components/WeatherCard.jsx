import React from 'react';
import { Cloud, CloudRain, Sun, Wind, Droplets, AlertTriangle } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';

const WeatherCard = ({ weather }) => {
  const getWeatherIcon = (condition) => {
    switch (condition.toLowerCase()) {
      case 'sunny':
        return <Sun className="w-8 h-8 theme-text-warning" />;
      case 'partly cloudy':
        return <Cloud className="w-8 h-8 theme-text-secondary" />;
      case 'rainy':
        return <CloudRain className="w-8 h-8 theme-text-accent-primary" />;
      default:
        return <Cloud className="w-8 h-8 theme-text-secondary" />;
    }
  };

  const getRiskBadgeVariant = (riskLevel) => {
    switch (riskLevel) {
      case 'LOW':
        return 'success';
      case 'MODERATE':
        return 'warning';
      case 'HIGH':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  const getStatusBorder = (condition) => {
    switch (condition.toLowerCase()) {
      case 'sunny':
        return 'border-t-theme-warning';
      case 'partly cloudy':
        return 'border-t-theme-secondary';
      case 'rainy':
        return 'border-t-theme-accent-primary';
      default:
        return 'border-t-theme-border';
    }
  };

  const formatLastUpdated = (date) => {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    return `${minutes} mins ago`;
  };

  return (
    <Card className={`theme-bg-secondary border-t-4 ${getStatusBorder(weather.condition)} transition-all duration-200`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold theme-text-primary transition-colors duration-200">
              {weather.temp}°C
            </span>
            {getWeatherIcon(weather.condition)}
          </div>
          <p className="text-sm theme-text-secondary mt-1 transition-colors duration-200">{weather.condition}</p>
        </div>
        
        <Badge variant={getRiskBadgeVariant(weather.riskLevel)}>
          {weather.riskLevel} RISK
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3">
        <div className="flex items-center gap-2">
          <Droplets className="w-4 h-4 theme-text-accent-primary" />
          <span className="text-sm theme-text-primary opacity-90 transition-colors duration-200">
            {weather.humidity}%
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Wind className="w-4 h-4 theme-text-secondary" />
          <span className="text-sm theme-text-primary opacity-90 transition-colors duration-200">
            {weather.windSpeed} km/h
          </span>
        </div>
      </div>

      <div className="text-xs theme-text-secondary opacity-70 transition-colors duration-200">
        Last updated {formatLastUpdated(weather.lastUpdated)}
      </div>
    </Card>
  );
};

export { WeatherCard };
