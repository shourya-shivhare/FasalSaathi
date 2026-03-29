import React from 'react';
import { Droplets, Clock, Calendar } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

import { useThemeStore } from '../../../stores/useThemeStore';

const IrrigationTimer = ({ irrigation }) => {
  const { theme } = useThemeStore();
  const isDark = theme === 'dark';

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatLastRun = (date) => {
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    return `${days} days ago`;
  };

  const prepareChartData = () => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return irrigation.weeklyUsage.map((usage, index) => ({
      day: days[index],
      usage: usage,
    }));
  };

  const chartColor = isDark ? '#6DBF5A' : '#4A7C3F';

  return (
    <Card className="transition-all duration-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Droplets className="w-5 h-5 theme-text-accent-primary" />
          <h3 className="text-lg font-semibold theme-text-primary transition-colors duration-200">Irrigation</h3>
        </div>
      </div>

      <div className="space-y-4">
        {/* Next Irrigation */}
        <div className="flex items-center justify-between p-3 theme-bg-secondary border theme-border rounded-lg transition-colors duration-200">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 theme-text-accent-primary" />
            <div>
              <div className="text-sm font-medium theme-text-primary transition-colors duration-200">
                Next irrigation
              </div>
              <div className="text-sm theme-text-secondary transition-colors duration-200">
                {formatDate(irrigation.nextScheduled)}
              </div>
            </div>
          </div>
        </div>

        {/* Start Irrigation Button */}
        <Button
          variant="primary"
          fullWidth
          size="lg"
        >
          Start Irrigation Now
        </Button>

        {/* Last Run Info */}
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2 theme-text-secondary transition-colors duration-200">
            <Clock className="w-4 h-4" />
            <span>Last run: {formatLastRun(irrigation.lastRun)}</span>
          </div>
          <span className="theme-text-secondary opacity-70 transition-colors duration-200">
            {irrigation.durationMins} mins
          </span>
        </div>

        {/* Weekly Water Usage Chart */}
        <div>
          <div className="text-sm font-medium theme-text-primary opacity-80 mb-2 transition-colors duration-200">
            Weekly Water Usage
          </div>
          <div className="h-24 w-full">
            <ResponsiveContainer width="100%" height={96}>
              <AreaChart data={prepareChartData()}>
                <defs>
                  <linearGradient id="colorUsage" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={chartColor} stopOpacity={0.8}/>
                    <stop offset="95%" stopColor={chartColor} stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <XAxis 
                  dataKey="day"
                  tick={{ fontSize: 10, fill: isDark ? '#9A9181' : '#5C5346' }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 10, fill: isDark ? '#9A9181' : '#5C5346' }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: isDark ? '#242B1E' : '#EDE5D0', 
                    border: `1px solid ${isDark ? '#3A4232' : '#D6CCB8'}`,
                    borderRadius: '0.5rem',
                    color: isDark ? '#EDE8DC' : '#1C1C1A'
                  }}
                  itemStyle={{ color: isDark ? '#EDE8DC' : '#1C1C1A' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="usage" 
                  stroke={chartColor} 
                  fillOpacity={1}
                  fill="url(#colorUsage)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </Card>
  );
};

export { IrrigationTimer };
