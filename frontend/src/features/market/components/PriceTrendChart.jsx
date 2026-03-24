import React from 'react';
import { Card } from '../../../components/ui/Card';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

const PriceTrendChart = ({ priceData, mspPrice, cropName }) => {
  const chartData = priceData.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    price: item.price,
    volume: item.volume,
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-stone-200 rounded-lg shadow-sm">
          <p className="text-sm font-medium text-stone-900 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.name === 'Price' ? `₹${entry.value}` : `${entry.value} tonnes`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <Card>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-stone-900">
          {cropName} - 30 Day Price Trend
        </h3>
        <p className="text-sm text-stone-600 mt-1">
          Daily mandi prices with trading volume
        </p>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f4" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }} 
              axisLine={false}
              tickLine={false}
            />
            <YAxis 
              yAxisId="price"
              tick={{ fontSize: 12 }} 
              axisLine={false}
              tickLine={false}
            />
            <YAxis 
              yAxisId="volume"
              orientation="right"
              tick={{ fontSize: 12 }} 
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
            <Legend />
            <ReferenceLine 
              y={mspPrice} 
              stroke="#dc2626" 
              strokeDasharray="5 5" 
              label={`MSP: ₹${mspPrice}`}
            />
            <Bar 
              yAxisId="volume"
              dataKey="volume" 
              fill="#e7e5e4"
            />
            <Line 
              yAxisId="price"
              type="monotone" 
              dataKey="price" 
              stroke="#16a34a" 
              strokeWidth={2}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
        <div className="text-center p-2 bg-stone-50 rounded">
          <div className="text-xs text-stone-600">Highest</div>
          <div className="font-semibold text-stone-900">
            ₹{Math.max(...priceData.map(d => d.price))}
          </div>
        </div>
        <div className="text-center p-2 bg-stone-50 rounded">
          <div className="text-xs text-stone-600">Average</div>
          <div className="font-semibold text-stone-900">
            ₹{Math.round(priceData.reduce((sum, d) => sum + d.price, 0) / priceData.length)}
          </div>
        </div>
        <div className="text-center p-2 bg-stone-50 rounded">
          <div className="text-xs text-stone-600">Lowest</div>
          <div className="font-semibold text-stone-900">
            ₹{Math.min(...priceData.map(d => d.price))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export { PriceTrendChart };
