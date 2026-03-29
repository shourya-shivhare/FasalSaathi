import React, { useState } from 'react';
import { AlertTriangle, Thermometer, Bug, Calendar } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
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

  const getAlertColorClasses = (type) => {
    switch (type) {
      case ALERT_TYPES.NUTRIENT_DEFICIENCY:
        return 'theme-text-warning theme-bg-warning/15';
      case ALERT_TYPES.WEATHER_WARNING:
        return 'theme-text-danger theme-bg-danger/15';
      case ALERT_TYPES.PEST_DETECTION:
        return 'theme-text-accent-secondary theme-bg-accent-secondary/15';
      case ALERT_TYPES.SCHEME_DEADLINE:
        return 'theme-text-accent-primary theme-bg-accent-primary/15';
      default:
        return 'theme-text-secondary theme-bg-surface-hover';
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
      <Card className="transition-all duration-200">
        <h3 className="text-lg font-semibold theme-text-primary mb-3 transition-colors duration-200">Alerts</h3>
        
        <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
          {alerts.map((alert) => {
            const Icon = getAlertIcon(alert.icon);
            const colorClasses = getAlertColorClasses(alert.type);
            
            return (
              <button
                key={alert.id}
                onClick={() => setSelectedAlert(alert)}
                className={`flex items-center gap-2 px-3 py-2 rounded-full border theme-border theme-bg-primary hover:theme-bg-surface-hover transition-all duration-200 flex-shrink-0 min-w-max shadow-sm`}
              >
                <div className={`p-1.5 rounded-full ${colorClasses} transition-colors duration-200`}>
                  <Icon className="w-3 h-3" />
                </div>
                <div className="text-left">
                  <div className="text-sm font-medium theme-text-primary transition-colors duration-200">
                    {alert.title}
                  </div>
                  <div className="text-[10px] theme-text-secondary opacity-70 transition-colors duration-200">
                    {formatTimestamp(alert.timestamp)}
                  </div>
                </div>
                <Badge variant={getSeverityBadge(alert.severity)} className="ml-1 scale-90">
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
              <div className={`p-3 rounded-full ${getAlertColorClasses(selectedAlert.type)} transition-colors duration-200`}>
                {React.createElement(getAlertIcon(selectedAlert.icon), {
                  className: 'w-6 h-6',
                })}
              </div>
              <div>
                <Badge variant={getSeverityBadge(selectedAlert.severity)}>
                  {selectedAlert.severity.toUpperCase()}
                </Badge>
                <div className="text-sm theme-text-secondary mt-1 transition-colors duration-200">
                  {formatTimestamp(selectedAlert.timestamp)}
                </div>
              </div>
            </div>
            
            <div className="theme-text-primary transition-colors duration-200">
              <p className="font-medium mb-2">Details</p>
              <p className="text-sm theme-text-secondary leading-relaxed">{selectedAlert.message}</p>
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
