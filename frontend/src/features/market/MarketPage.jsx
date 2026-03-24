import React from 'react';
import { TrendingUp } from 'lucide-react';
import { TopBar } from '../../components/layout/TopBar';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { MandiPriceCard } from './components/MandiPriceCard';
import { MSPPriceTable } from './components/MSPPriceTable';
import { PriceTrendChart } from './components/PriceTrendChart';
import { useFieldStore } from '../../stores/useFieldStore.jsx';
import { mockMandiPrices, mockMSPPrices } from '../../lib/mockData.jsx';

const MarketPage = () => {
  const { getActiveField } = useFieldStore();
  const activeField = getActiveField();

  // Mock data for demonstration
  const currentCrop = activeField?.crop || 'Wheat';
  const currentPrice = 3040;
  const mspPrice = 2275;
  const mandiName = 'Narela Mandi';
  const distance = 5;

  // Generate 30-day price history from the 7-day mock data
  const generate30DayData = () => {
    const baseData = mockMandiPrices;
    const extendedData = [];
    
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      // Use base data for last 7 days, generate synthetic data for earlier days
      let price, volume;
      if (i < 7) {
        const baseItem = baseData[6 - i];
        price = baseItem.price;
        volume = baseItem.volume;
      } else {
        // Generate synthetic data with some variation
        const basePrice = 2900;
        const variation = Math.sin(i * 0.3) * 200 + Math.random() * 100;
        price = Math.round(basePrice + variation);
        volume = Math.round(800 + Math.random() * 600);
      }
      
      extendedData.push({
        date: date.toISOString().split('T')[0],
        price,
        volume,
      });
    }
    
    return extendedData;
  };

  const priceHistory = generate30DayData();

  return (
    <PageWrapper>
      <TopBar
        icon={TrendingUp}
        title="Market Prices"
        subtitle={activeField ? `${currentCrop} prices` : 'Latest market rates'}
      />

      <div className="p-4 space-y-4">
        {/* Current Mandi Price Card */}
        <MandiPriceCard
          crop={currentCrop}
          currentPrice={currentPrice}
          mspPrice={mspPrice}
          priceHistory={mockMandiPrices}
          mandiName={mandiName}
          distance={distance}
        />

        {/* 30-Day Price Trend Chart */}
        <PriceTrendChart
          priceData={priceHistory}
          mspPrice={mspPrice}
          cropName={currentCrop}
        />

        {/* MSP Price Table */}
        <MSPPriceTable mspData={mockMSPPrices} />

        {/* Market Insights */}
        <div className="info-banner">
          <h4 className="font-semibold text-green-800 mb-2 flex items-center gap-2">
            📊 Market Insights
          </h4>
          <ul className="text-sm text-green-700 space-y-1">
            <li>• {currentCrop} prices are {currentPrice > mspPrice ? 'above' : 'below'} MSP by ₹{Math.abs(currentPrice - mspPrice)}/quintal</li>
            <li>• Prices have shown {priceHistory[priceHistory.length - 1].price > priceHistory[0].price ? 'an upward 📈' : 'a downward 📉'} trend over the past month</li>
            <li>• Trading volume has been {priceHistory[priceHistory.length - 1].volume > priceHistory[0].volume ? 'increasing' : 'decreasing'} recently</li>
            <li>• Best time to sell: Consider market conditions and storage costs</li>
          </ul>
        </div>
      </div>
    </PageWrapper>
  );
};

export { MarketPage };
