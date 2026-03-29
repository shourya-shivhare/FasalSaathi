import React from 'react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { CheckCircle, Calendar, Bug, ExternalLink, TrendingUp, Droplets, Camera } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ACTION_CARD_TYPES } from '../../../lib/constants.jsx';

const ActionCard = ({ actionCard }) => {
  const navigate = useNavigate();

  const renderScanCard = (data) => (
    <Card className="border-l-4 border-l-theme-accent-primary transition-all duration-300 bg-gradient-to-br from-theme-bg-secondary to-theme-accent-primary/5 p-4">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl theme-bg-surface flex items-center justify-center border theme-border">
          <Bug className="w-6 h-6 theme-text-accent-primary" />
        </div>
        <div>
          <h4 className="font-bold theme-text-primary leading-tight">{data.title || 'Pest Detection'}</h4>
          <p className="text-xs theme-text-secondary">{data.subtitle || 'Scan your crop for pests'}</p>
        </div>
      </div>
      
      <div className="space-y-4">
        <div className="p-3 theme-bg-surface-hover rounded-xl border theme-border border-dashed">
          <p className="text-xs theme-text-secondary leading-relaxed">
            {data.description || 'Take a clear photo of the affected area. Our AI will identify the pest and suggest treatments.'}
          </p>
        </div>
        
        <Button 
          variant="primary" 
          size="sm" 
          icon={Camera} 
          fullWidth
          onClick={() => navigate('/scan')}
        >
          Open Camera & Scan
        </Button>
      </div>
    </Card>
  );

  const renderFertilizerCard = (data) => (
    <Card className="border-l-4 border-l-theme-success transition-all duration-200">
      <div className="flex items-center gap-2 mb-3">
        <Droplets className="w-5 h-5 theme-text-success" />
        <h4 className="font-semibold theme-text-primary">Fertilizer Recommendation</h4>
      </div>
      
      <div className="space-y-3">
        <div className="space-y-2">
          {data.nutrients.map((nutrient) => (
            <div key={nutrient.name} className="flex justify-between items-center px-1">
              <span className="text-sm theme-text-secondary">{nutrient.name}</span>
              <div className="text-right">
                <span className="text-sm font-medium theme-text-primary">
                  {nutrient.current} / {nutrient.recommended} {nutrient.unit}
                </span>
                <div className="text-xs theme-text-secondary opacity-80">
                  {nutrient.current < nutrient.recommended ? 'Low' : 'Good'}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="theme-bg-secondary p-3 rounded-lg border theme-border transition-colors duration-200">
          <p className="text-sm theme-text-success font-medium mb-1">Recommendation:</p>
          <p className="text-sm theme-text-primary">{data.recommendation}</p>
          <div className="mt-2 text-xs theme-text-secondary">
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
    <Card className="border-l-4 border-l-theme-accent-primary transition-all duration-200">
      <div className="flex items-center gap-2 mb-3">
        <Droplets className="w-5 h-5 theme-text-accent-primary" />
        <h4 className="font-semibold theme-text-primary">Irrigation Schedule</h4>
      </div>
      
      <div className="space-y-3">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b theme-border">
                <th className="text-left py-2 theme-text-secondary">Day</th>
                <th className="text-left py-2 theme-text-secondary">Time</th>
                <th className="text-left py-2 theme-text-secondary">Duration</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b theme-border opacity-70">
                <td className="py-2 theme-text-primary">Today</td>
                <td className="py-2 theme-text-primary">6:00 AM</td>
                <td className="py-2 theme-text-primary">45 mins</td>
              </tr>
              <tr className="border-b theme-border opacity-70">
                <td className="py-2 theme-text-primary">Tomorrow</td>
                <td className="py-2 theme-text-primary">6:00 AM</td>
                <td className="py-2 theme-text-primary">40 mins</td>
              </tr>
              <tr>
                <td className="py-2 theme-text-primary">Day 3</td>
                <td className="py-2 theme-text-primary">6:00 AM</td>
                <td className="py-2 theme-text-primary">50 mins</td>
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
    <Card className="border-l-4 border-l-theme-danger transition-all duration-200">
      <div className="flex items-center gap-2 mb-3">
        <Bug className="w-5 h-5 theme-text-danger" />
        <h4 className="font-semibold theme-text-primary">Pest Alert</h4>
      </div>
      
      <div className="space-y-3">
        <div>
          <span className="text-sm font-medium theme-text-primary">Pest:</span>
          <span className="text-sm theme-text-secondary ml-2">{data.pestName}</span>
        </div>
        
        <div>
          <span className="text-sm font-medium theme-text-primary">Affected Crop:</span>
          <span className="text-sm theme-text-secondary ml-2">{data.affectedCrop}</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium theme-text-primary">Severity:</span>
          <Badge variant={data.severity === 'High' ? 'danger' : data.severity === 'Medium' ? 'warning' : 'info'}>
            {data.severity}
          </Badge>
        </div>
        
        <div>
          <span className="text-sm font-medium theme-text-primary">Affected Area:</span>
          <span className="text-sm theme-text-secondary ml-2">{data.affectedArea}%</span>
        </div>
        
        <Button variant="outline" size="sm" fullWidth>
          View Treatment Guide
        </Button>
      </div>
    </Card>
  );

  const renderSchemeCard = (data) => (
    <Card className="border-l-4 border-l-theme-accent-primary transition-all duration-200">
      <div className="flex items-center gap-2 mb-3">
        <Calendar className="w-5 h-5 theme-text-accent-primary" />
        <h4 className="font-semibold theme-text-primary">Government Scheme</h4>
      </div>
      
      <div className="space-y-3">
        <div>
          <h5 className="font-medium theme-text-primary">{data.schemeName}</h5>
          <p className="text-sm theme-text-secondary">{data.ministry}</p>
        </div>
        
        <div className="text-lg font-semibold theme-text-success">
          {data.benefit}
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium theme-text-primary">Deadline:</span>
          <Badge variant="danger">
            {data.deadline}
          </Badge>
        </div>
        
        <div>
          <span className="text-sm font-medium theme-text-primary">Eligibility:</span>
          <ul className="mt-1 space-y-1">
            {data.eligibility.map((item, index) => (
              <li key={index} className="text-sm theme-text-secondary flex items-start gap-2">
                <span className="theme-text-success mt-0.5">•</span>
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
    <Card className="border-l-4 border-l-theme-warning transition-all duration-200">
      <div className="flex items-center gap-2 mb-3">
        <TrendingUp className="w-5 h-5 theme-text-warning" />
        <h4 className="font-semibold theme-text-primary">Market Price Update</h4>
      </div>
      
      <div className="space-y-3">
        <div>
          <span className="text-sm font-medium theme-text-primary">Crop:</span>
          <span className="text-sm theme-text-secondary ml-2">{data.cropName}</span>
        </div>
        
        <div className="text-2xl font-bold theme-text-primary">
          ₹{data.todayPrice}/quintal
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm theme-text-secondary">MSP: </span>
            <span className="text-sm font-medium theme-text-primary">₹{data.mspPrice}/quintal</span>
          </div>
          <div className="flex items-center gap-1">
            {data.trend === 'up' ? (
              <TrendingUp className="w-4 h-4 theme-text-success" />
            ) : (
              <TrendingUp className="w-4 h-4 theme-text-danger rotate-180" />
            )}
            <span className={`text-sm font-medium ${data.trend === 'up' ? 'theme-text-success' : 'theme-text-danger'}`}>
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
    case ACTION_CARD_TYPES.SCAN:
      return renderScanCard(actionCard.data);
    default:
      return null;
  }
};

export { ActionCard };
