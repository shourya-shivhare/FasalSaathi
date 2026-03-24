import React, { useState } from 'react';
import { AlertTriangle, Thermometer, Bug, Calendar } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Modal } from '../../../components/ui/Modal';
import { ALERT_TYPES } from '../../../lib/constants.jsx';

const AlertsFeed = ({ alerts }) => {
  const [selectedAlert, setSelectedAlert] = useState(null);

  const getAlertIcon = (iconName) => {
    const icons = {
      AlertTriangle,
      Thermometer,
      Bug,
      Calendar,
    };
    return icons[iconName] || AlertTriangle;
  };

  const getAlertColor = (type) => {
    switch (type) {
      case ALERT_TYPES.NUTRIENT_DEFICIENCY:
        return 'text-amber-600 bg-amber-50';
      case ALERT_TYPES.WEATHER_WARNING:
        return 'text-red-600 bg-red-50';
      case ALERT_TYPES.PEST_DETECTION:
        return 'text-purple-600 bg-purple-50';
      case ALERT_TYPES.SCHEME_DEADLINE:
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-stone-600 bg-stone-50';
    }
  };

  const getSeverityBadge = (severity) => {
    const variants = {
      high: 'danger',
      medium: 'warning',
      low: 'info',
    };
    return variants[severity] || 'neutral';
  };

  const formatTimestamp = (date) => {
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / (60 * 60 * 1000));
    
    if (hours < 1) {
      const minutes = Math.floor(diff / (60 * 1000));
      return `${minutes}m ago`;
    }
    if (hours < 24) {
      return `${hours}h ago`;
    }
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <>
      <Card>
        <h3 className="text-lg font-semibold text-stone-900 mb-3">Alerts</h3>
        
        <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
          {alerts.map((alert) => {
            const Icon = getAlertIcon(alert.icon);
            const colorClass = getAlertColor(alert.type);
            
            return (
              <button
                key={alert.id}
                onClick={() => setSelectedAlert(alert)}
                className={`flex items-center gap-2 px-3 py-2 rounded-full border border-stone-200 bg-white hover:bg-stone-50 transition-colors flex-shrink-0 min-w-max`}
              >
                <div className={`p-1.5 rounded-full ${colorClass}`}>
                  <Icon className="w-3 h-3" />
                </div>
                <div className="text-left">
                  <div className="text-sm font-medium text-stone-900">
                    {alert.title}
                  </div>
                  <div className="text-xs text-stone-500">
                    {formatTimestamp(alert.timestamp)}
                  </div>
                </div>
                <Badge variant={getSeverityBadge(alert.severity)} className="ml-1">
                  {alert.severity}
                </Badge>
              </button>
            );
          })}
        </div>
      </Card>

      {/* Alert Detail Modal */}
      <Modal
        isOpen={!!selectedAlert}
        onClose={() => setSelectedAlert(null)}
        title={selectedAlert?.title}
        size="sm"
      >
        {selectedAlert && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-full ${getAlertColor(selectedAlert.type)}`}>
                {React.createElement(getAlertIcon(selectedAlert.icon), {
                  className: 'w-6 h-6',
                })}
              </div>
              <div>
                <Badge variant={getSeverityBadge(selectedAlert.severity)}>
                  {selectedAlert.severity.toUpperCase()}
                </Badge>
                <div className="text-sm text-stone-500 mt-1">
                  {formatTimestamp(selectedAlert.timestamp)}
                </div>
              </div>
            </div>
            
            <div className="text-stone-700">
              <p className="font-medium mb-2">Details</p>
              <p className="text-sm leading-relaxed">{selectedAlert.message}</p>
            </div>
            
            <div className="flex gap-3 pt-2">
              <Button variant="primary" size="sm" className="flex-1">
                Take Action
              </Button>
              <Button variant="outline" size="sm" className="flex-1">
                Dismiss
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
};

export { AlertsFeed };
