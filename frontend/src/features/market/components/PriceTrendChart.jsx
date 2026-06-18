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
        <div style={{
          background: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '12px',
          padding: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          color: 'var(--color-text-primary)'
        }}>
          <p style={{ fontSize: '0.875rem', fontWeight: 600, margin: '0 0 8px', color: 'var(--color-text-primary)' }}>{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ fontSize: '0.85rem', margin: '4px 0', color: entry.name === 'Price' ? 'var(--color-accent-primary)' : 'var(--color-text-secondary)' }}>
              {entry.name}: {entry.name === 'Price' ? `₹${entry.value}` : `${entry.value} tonnes`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <Card style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }}>
      <div style={{ marginBottom: '16px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
          {cropName} - 30 Day Price Trend
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginTop: '4px', margin: 0 }}>
          Daily mandi prices with trading volume
        </p>
      </div>

      <div style={{ height: '320px', width: '100%' }}>
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 11, fill: 'var(--color-text-secondary)' }} 
              axisLine={false}
              tickLine={false}
            />
            <YAxis 
              yAxisId="price"
              tick={{ fontSize: 11, fill: 'var(--color-text-secondary)' }} 
              axisLine={false}
              tickLine={false}
            />
            <YAxis 
              yAxisId="volume"
              orientation="right"
              tick={{ fontSize: 11, fill: 'var(--color-text-secondary)' }} 
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '11px', color: 'var(--color-text-primary)' }} />
            <ReferenceLine 
              yAxisId="price"
              y={mspPrice} 
              stroke="var(--color-danger)" 
              strokeDasharray="5 5" 
              label={{ value: `MSP: ₹${mspPrice}`, fill: 'var(--color-danger)', fontSize: 11, position: 'top' }}
            />
            <Bar 
              yAxisId="volume"
              dataKey="volume" 
              fill="var(--color-section-header-bg)"
              name="Volume"
              radius={[4, 4, 0, 0]}
            />
            <Line 
              yAxisId="price"
              type="monotone" 
              dataKey="price" 
              stroke="var(--color-accent-primary)" 
              strokeWidth={2.5}
              name="Price"
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', fontSize: '0.85rem' }}>
        <div style={{ textAlign: 'center', padding: '10px', background: 'var(--color-bg-primary)', borderRadius: '12px', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>Highest</div>
          <div style={{ fontWeight: 700, color: 'var(--color-text-primary)' }}>
            ₹{priceData.length > 0 ? Math.max(...priceData.map(d => d.price)).toLocaleString() : 0}
          </div>
        </div>
        <div style={{ textAlign: 'center', padding: '10px', background: 'var(--color-bg-primary)', borderRadius: '12px', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>Average</div>
          <div style={{ fontWeight: 700, color: 'var(--color-text-primary)' }}>
            ₹{priceData.length > 0 ? Math.round(priceData.reduce((sum, d) => sum + d.price, 0) / priceData.length).toLocaleString() : 0}
          </div>
        </div>
        <div style={{ textAlign: 'center', padding: '10px', background: 'var(--color-bg-primary)', borderRadius: '12px', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginBottom: '2px' }}>Lowest</div>
          <div style={{ fontWeight: 700, color: 'var(--color-text-primary)' }}>
            ₹{priceData.length > 0 ? Math.min(...priceData.map(d => d.price)).toLocaleString() : 0}
          </div>
        </div>
      </div>
    </Card>
  );
};

export { PriceTrendChart };
