import React from 'react';
import { MapPin, Eye, Wheat, Sprout, Flower2, TreePine } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { ProgressBar } from '../../../components/ui/ProgressBar';

const FieldCard = ({ field, onViewDetails, isActive = false }) => {
  const getCropIcon = (crop) => {
    const cropIcons = {
      Wheat: Wheat,
      Rice: Sprout,
      Cotton: Flower2,
      Soybean: TreePine,
      Maize: Sprout,
    };
    const Icon = cropIcons[crop] || Sprout;
    return <Icon className="w-5 h-5" />;
  };

  const getSoilHealthColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'amber';
    return 'red';
  };

  const getSoilHealthLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Attention';
  };

  return (
    <Card className={`p-4 ${isActive ? 'border-l-4 border-l-brand-500' : ''}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-stone-100 rounded-lg">
            {getCropIcon(field.crop)}
          </div>
          <div>
            <h3 className="font-semibold text-stone-900">{field.name}</h3>
            <div className="flex items-center gap-1 text-sm text-stone-500 mt-1">
              <MapPin className="w-3 h-3" />
              {field.location.village}
            </div>
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          icon={Eye}
          onClick={() => onViewDetails(field)}
        >
          View
        </Button>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-stone-600">Area</span>
          <span className="text-sm font-medium text-stone-900">
            {field.area} {field.areaUnit}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-stone-600">Crop</span>
          <div className="flex items-center gap-2">
            {getCropIcon(field.crop)}
            <span className="text-sm font-medium text-stone-900">{field.crop}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-stone-600">Growth Stage</span>
          <Badge variant="info">{field.growthStage}</Badge>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-stone-600">Soil Health</span>
            <Badge variant={getSoilHealthColor(field.soilHealth.score) === 'green' ? 'success' : getSoilHealthColor(field.soilHealth.score) === 'amber' ? 'warning' : 'danger'}>
              {getSoilHealthLabel(field.soilHealth.score)}
            </Badge>
          </div>
          <ProgressBar
            value={field.soilHealth.score}
            colorScheme={getSoilHealthColor(field.soilHealth.score)}
            className="h-2"
          />
        </div>

        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="text-center p-2 bg-stone-50 rounded">
            <div className="font-medium text-stone-900">N</div>
            <div className="text-stone-600">{field.soilHealth.N}</div>
          </div>
          <div className="text-center p-2 bg-stone-50 rounded">
            <div className="font-medium text-stone-900">P</div>
            <div className="text-stone-600">{field.soilHealth.P}</div>
          </div>
          <div className="text-center p-2 bg-stone-50 rounded">
            <div className="font-medium text-stone-900">K</div>
            <div className="text-stone-600">{field.soilHealth.K}</div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export { FieldCard };
