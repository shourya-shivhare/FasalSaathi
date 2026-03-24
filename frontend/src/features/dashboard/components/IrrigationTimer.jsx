import React from 'react';
import { Droplets, Clock, Calendar } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const IrrigationTimer = ({ irrigation }) => {
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

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Droplets className="w-5 h-5 text-blue-500" />
          <h3 className="text-lg font-semibold text-stone-900">Irrigation</h3>
        </div>
      </div>

      <div className="space-y-4">
        {/* Next Irrigation */}
        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-blue-600" />
            <div>
              <div className="text-sm font-medium text-stone-900">
                Next irrigation
              </div>
              <div className="text-sm text-stone-600">
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
          className="bg-green-600 hover:bg-green-700"
        >
          Start Irrigation Now
        </Button>

        {/* Last Run Info */}
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2 text-stone-600">
            <Clock className="w-4 h-4" />
            <span>Last run: {formatLastRun(irrigation.lastRun)}</span>
          </div>
          <span className="text-stone-500">
            {irrigation.durationMins} mins
          </span>
        </div>

        {/* Weekly Water Usage Chart */}
        <div>
          <div className="text-sm font-medium text-stone-700 mb-2">
            Weekly Water Usage
          </div>
          <div className="h-24 w-full">
            <ResponsiveContainer width="100%" height={96}>
              <AreaChart data={prepareChartData()}>
                <defs>
                  <linearGradient id="colorUsage" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#16a34a" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#16a34a" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <XAxis 
                  dataKey="day"
                  tick={{ fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#f5f5f4', 
                    border: '1px solid #e7e5e4',
                    borderRadius: '0.5rem'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="usage" 
                  stroke="#16a34a" 
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
