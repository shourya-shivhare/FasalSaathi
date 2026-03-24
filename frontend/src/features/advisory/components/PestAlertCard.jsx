import React from 'react';
import { Bug, AlertTriangle } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';

const PestAlertCard = ({ pestAlert }) => {
  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'neutral';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'medium':
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case 'low':
        return <Bug className="w-4 h-4 text-blue-500" />;
      default:
        return <Bug className="w-4 h-4 text-stone-500" />;
    }
  };

  return (
    <Card className="border-l-4 border-l-red-500">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-50 rounded-lg">
            <Bug className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <h3 className="font-semibold text-stone-900">{pestAlert.pestName}</h3>
            <p className="text-sm text-stone-600">Affects {pestAlert.affectedCrop}</p>
          </div>
        </div>
        
        <Badge variant={getSeverityColor(pestAlert.severity)}>
          {pestAlert.severity}
        </Badge>
      </div>

      <div className="space-y-3">
        <div>
          <span className="text-sm font-medium text-stone-700">Affected Regions:</span>
          <div className="mt-1 flex flex-wrap gap-1">
            {pestAlert.affectedStates.map((state, index) => (
              <span
                key={index}
                className="inline-block px-2 py-1 bg-stone-100 text-xs text-stone-700 rounded"
              >
                {state}
              </span>
            ))}
          </div>
        </div>

        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            {getSeverityIcon(pestAlert.severity)}
            <span className="text-sm font-medium text-amber-800">Prevention Tip</span>
          </div>
          <p className="text-sm text-amber-700">{pestAlert.preventionTip}</p>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="p-2 bg-stone-50 rounded">
            <span className="text-stone-600">Risk Level:</span>
            <div className="font-medium text-stone-900">{pestAlert.severity}</div>
          </div>
          <div className="p-2 bg-stone-50 rounded">
            <span className="text-stone-600">Action:</span>
            <div className="font-medium text-stone-900">Monitor</div>
          </div>
        </div>

        <Button variant="outline" size="sm" fullWidth>
          Report Sighting
        </Button>
      </div>
    </Card>
  );
};

export { PestAlertCard };
