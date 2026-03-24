import React from 'react';
import { TrendingUp, TrendingDown, MapPin } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MandiPriceCard = ({ crop, currentPrice, mspPrice, priceHistory, mandiName, distance }) => {
  const latestPrice = priceHistory[priceHistory.length - 1];
  const previousPrice = priceHistory[priceHistory.length - 2];
  const priceChange = latestPrice.price - previousPrice.price;
  const priceChangePercent = ((priceChange / previousPrice.price) * 100).toFixed(1);
  const mspDifference = currentPrice - mspPrice;
  const mspDifferencePercent = ((mspDifference / mspPrice) * 100).toFixed(1);

  const chartData = priceHistory.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    price: item.price,
  }));

  const TrendIcon = priceChange >= 0 ? TrendingUp : TrendingDown;
  const trendColor = priceChange >= 0 ? 'text-green-500' : 'text-red-500';

  return (
    <Card className="border-l-4 border-l-amber-500">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-stone-900">{crop}</h3>
          <div className="flex items-center gap-2 text-sm text-stone-600 mt-1">
            <MapPin className="w-3 h-3" />
            <span>{mandiName}</span>
            <span>•</span>
            <span>{distance} km</span>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-2xl font-bold text-stone-900">
            ₹{currentPrice}
          </div>
          <div className="text-xs text-stone-500">per quintal</div>
        </div>
      </div>

      {/* Price Trend */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-stone-600">7-Day Trend</span>
          <div className={`flex items-center gap-1 ${trendColor}`}>
            <TrendIcon className="w-4 h-4" />
            <span className="text-sm font-medium">
              {priceChange >= 0 ? '+' : ''}{priceChangePercent}%
            </span>
          </div>
        </div>
        
        <div className="h-24 w-full">
          <ResponsiveContainer width="100%" height={96}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f4" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 10 }} 
                axisLine={false}
                tickLine={false}
              />
              <YAxis 
                tick={{ fontSize: 10 }} 
                axisLine={false}
                tickLine={false}
                domain={['dataMin - 10', 'dataMax + 10']}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#f5f5f4', 
                  border: '1px solid #e7e5e4',
                  borderRadius: '0.5rem'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#16a34a" 
                strokeWidth={2}
                dot={{ fill: '#f59e0b', r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* MSP Comparison */}
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center p-3 bg-stone-50 rounded-lg">
          <div className="text-xs text-stone-600 mb-1">Current Price</div>
          <div className="text-lg font-semibold text-stone-900">₹{currentPrice}</div>
        </div>
        
        <div className="text-center p-3 bg-stone-50 rounded-lg">
          <div className="text-xs text-stone-600 mb-1">MSP Price</div>
          <div className="text-lg font-semibold text-stone-900">₹{mspPrice}</div>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <Badge variant={mspDifference >= 0 ? 'success' : 'danger'}>
          {mspDifference >= 0 ? '↑' : '↓'} {Math.abs(mspDifferencePercent)}% vs MSP
        </Badge>
        
        <div className="text-sm text-stone-600">
          {mspDifference >= 0 ? '+' : ''}₹{Math.abs(mspDifference)} difference
        </div>
      </div>
    </Card>
  );
};

export { MandiPriceCard };
