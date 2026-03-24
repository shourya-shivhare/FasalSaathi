import React from 'react';
import { Cloud, CloudRain, Sun, Wind, Droplets, AlertTriangle } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';

const WeatherCard = ({ weather }) => {
  const getWeatherIcon = (condition) => {
    switch (condition.toLowerCase()) {
      case 'sunny':
        return <Sun className="w-8 h-8 text-amber-500" />;
      case 'partly cloudy':
        return <Cloud className="w-8 h-8 text-stone-400" />;
      case 'rainy':
        return <CloudRain className="w-8 h-8 text-blue-500" />;
      default:
        return <Cloud className="w-8 h-8 text-stone-400" />;
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

  const getBackgroundGradient = (condition) => {
    switch (condition.toLowerCase()) {
      case 'sunny':
        return 'bg-gradient-to-br from-amber-50 to-orange-50';
      case 'partly cloudy':
        return 'bg-gradient-to-br from-stone-50 to-stone-100';
      case 'rainy':
        return 'bg-gradient-to-br from-blue-50 to-stone-100';
      default:
        return 'bg-gradient-to-br from-stone-50 to-stone-100';
    }
  };

  const formatLastUpdated = (date) => {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    return `${minutes} mins ago`;
  };

  return (
    <Card className={`${getBackgroundGradient(weather.condition)} border-none`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold text-stone-900">
              {weather.temp}°C
            </span>
            {getWeatherIcon(weather.condition)}
          </div>
          <p className="text-sm text-stone-600 mt-1">{weather.condition}</p>
        </div>
        
        <Badge variant={getRiskBadgeVariant(weather.riskLevel)}>
          {weather.riskLevel} RISK
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3">
        <div className="flex items-center gap-2">
          <Droplets className="w-4 h-4 text-blue-500" />
          <span className="text-sm text-stone-700">
            {weather.humidity}%
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Wind className="w-4 h-4 text-stone-500" />
          <span className="text-sm text-stone-700">
            {weather.windSpeed} km/h
          </span>
        </div>
      </div>

      <div className="text-xs text-stone-500">
        Last updated {formatLastUpdated(weather.lastUpdated)}
      </div>
    </Card>
  );
};

export { WeatherCard };
