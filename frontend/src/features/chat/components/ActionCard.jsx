import React from 'react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { CheckCircle, Calendar, Bug, ExternalLink, TrendingUp, Droplets } from 'lucide-react';
import { ACTION_CARD_TYPES } from '../../../lib/constants.jsx';

const ActionCard = ({ actionCard }) => {
  const renderFertilizerCard = (data) => (
    <Card className="border-l-4 border-l-green-500">
      <div className="flex items-center gap-2 mb-3">
        <Droplets className="w-5 h-5 text-green-600" />
        <h4 className="font-semibold text-stone-900">Fertilizer Recommendation</h4>
      </div>
      
      <div className="space-y-3">
        <div className="space-y-2">
          {data.nutrients.map((nutrient) => (
            <div key={nutrient.name} className="flex justify-between items-center">
              <span className="text-sm text-stone-600">{nutrient.name}</span>
              <div className="text-right">
                <span className="text-sm font-medium text-stone-900">
                  {nutrient.current} / {nutrient.recommended} {nutrient.unit}
                </span>
                <div className="text-xs text-stone-500">
                  {nutrient.current < nutrient.recommended ? 'Low' : 'Good'}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="bg-green-50 p-3 rounded-lg">
          <p className="text-sm text-green-800 font-medium mb-1">Recommendation:</p>
          <p className="text-sm text-green-700">{data.recommendation}</p>
          <div className="mt-2 text-xs text-green-600">
            <span className="font-medium">Product:</span> {data.fertilizer} | 
            <span className="font-medium"> Rate:</span> {data.applicationRate} | 
            <span className="font-medium"> Time:</span> {data.timing}
          </div>
        </div>
        
        <Button variant="primary" size="sm" icon={CheckCircle} fullWidth>
          ✓ Mark as Applied
        </Button>
      </div>
    </Card>
  );

  const renderIrrigationCard = (data) => (
    <Card className="border-l-4 border-l-blue-500">
      <div className="flex items-center gap-2 mb-3">
        <Droplets className="w-5 h-5 text-blue-600" />
        <h4 className="font-semibold text-stone-900">Irrigation Schedule</h4>
      </div>
      
      <div className="space-y-3">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-stone-200">
                <th className="text-left py-2 text-stone-600">Day</th>
                <th className="text-left py-2 text-stone-600">Time</th>
                <th className="text-left py-2 text-stone-600">Duration</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-stone-100">
                <td className="py-2">Today</td>
                <td className="py-2">6:00 AM</td>
                <td className="py-2">45 mins</td>
              </tr>
              <tr className="border-b border-stone-100">
                <td className="py-2">Tomorrow</td>
                <td className="py-2">6:00 AM</td>
                <td className="py-2">40 mins</td>
              </tr>
              <tr>
                <td className="py-2">Day 3</td>
                <td className="py-2">6:00 AM</td>
                <td className="py-2">50 mins</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <Button variant="primary" size="sm" icon={Calendar} fullWidth>
          📅 Schedule Irrigation
        </Button>
      </div>
    </Card>
  );

  const renderPestAlertCard = (data) => (
    <Card className="border-l-4 border-l-red-500">
      <div className="flex items-center gap-2 mb-3">
        <Bug className="w-5 h-5 text-red-600" />
        <h4 className="font-semibold text-stone-900">Pest Alert</h4>
      </div>
      
      <div className="space-y-3">
        <div>
          <span className="text-sm font-medium text-stone-900">Pest:</span>
          <span className="text-sm text-stone-600 ml-2">{data.pestName}</span>
        </div>
        
        <div>
          <span className="text-sm font-medium text-stone-900">Affected Crop:</span>
          <span className="text-sm text-stone-600 ml-2">{data.affectedCrop}</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-stone-900">Severity:</span>
          <Badge variant={data.severity === 'High' ? 'danger' : data.severity === 'Medium' ? 'warning' : 'info'}>
            {data.severity}
          </Badge>
        </div>
        
        <div>
          <span className="text-sm font-medium text-stone-900">Affected Area:</span>
          <span className="text-sm text-stone-600 ml-2">{data.affectedArea}%</span>
        </div>
        
        <Button variant="outline" size="sm" fullWidth>
          View Treatment Guide
        </Button>
      </div>
    </Card>
  );

  const renderSchemeCard = (data) => (
    <Card className="border-l-4 border-l-blue-500">
      <div className="flex items-center gap-2 mb-3">
        <Calendar className="w-5 h-5 text-blue-600" />
        <h4 className="font-semibold text-stone-900">Government Scheme</h4>
      </div>
      
      <div className="space-y-3">
        <div>
          <h5 className="font-medium text-stone-900">{data.schemeName}</h5>
          <p className="text-sm text-stone-600">{data.ministry}</p>
        </div>
        
        <div className="text-lg font-semibold text-green-600">
          {data.benefit}
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-stone-900">Deadline:</span>
          <Badge variant="danger">
            {data.deadline}
          </Badge>
        </div>
        
        <div>
          <span className="text-sm font-medium text-stone-900">Eligibility:</span>
          <ul className="mt-1 space-y-1">
            {data.eligibility.map((item, index) => (
              <li key={index} className="text-sm text-stone-600 flex items-start gap-2">
                <span className="text-green-500 mt-0.5">•</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
        
        <Button variant="primary" size="sm" icon={ExternalLink} fullWidth>
          Apply Now →
        </Button>
      </div>
    </Card>
  );

  const renderMarketPriceCard = (data) => (
    <Card className="border-l-4 border-l-amber-500">
      <div className="flex items-center gap-2 mb-3">
        <TrendingUp className="w-5 h-5 text-amber-600" />
        <h4 className="font-semibold text-stone-900">Market Price Update</h4>
      </div>
      
      <div className="space-y-3">
        <div>
          <span className="text-sm font-medium text-stone-900">Crop:</span>
          <span className="text-sm text-stone-600 ml-2">{data.cropName}</span>
        </div>
        
        <div className="text-2xl font-bold text-stone-900">
          ₹{data.todayPrice}/quintal
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm text-stone-600">MSP: </span>
            <span className="text-sm font-medium text-stone-900">₹{data.mspPrice}/quintal</span>
          </div>
          <div className="flex items-center gap-1">
            {data.trend === 'up' ? (
              <TrendingUp className="w-4 h-4 text-green-500" />
            ) : (
              <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />
            )}
            <span className={`text-sm font-medium ${data.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
              {data.difference > 0 ? '+' : ''}{data.difference}%
            </span>
          </div>
        </div>
        
        <Button variant="outline" size="sm" fullWidth>
          Find Nearest Mandi
        </Button>
      </div>
    </Card>
  );

  switch (actionCard.type) {
    case ACTION_CARD_TYPES.FERTILIZER:
      return renderFertilizerCard(actionCard.data);
    case ACTION_CARD_TYPES.IRRIGATION:
      return renderIrrigationCard(actionCard.data);
    case ACTION_CARD_TYPES.PEST_ALERT:
      return renderPestAlertCard(actionCard.data);
    case ACTION_CARD_TYPES.SCHEME:
      return renderSchemeCard(actionCard.data);
    case ACTION_CARD_TYPES.MARKET_PRICE:
      return renderMarketPriceCard(actionCard.data);
    default:
      return null;
  }
};

export { ActionCard };
