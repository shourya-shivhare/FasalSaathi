import React from 'react';
import { Calendar, ExternalLink, CheckCircle } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';

const SchemeCard = ({ scheme }) => {
  const getDaysUntilDeadline = (deadline) => {
    if (!deadline) return null;
    const now = new Date();
    const diff = deadline - now;
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return days;
  };

  const getDeadlineColor = (days) => {
    if (days === null) return 'neutral';
    if (days < 0) return 'danger';
    if (days < 30) return 'danger';
    if (days < 60) return 'warning';
    return 'success';
  };

  const getDeadlineText = (days) => {
    if (days === null) return 'No deadline';
    if (days < 0) return 'Expired';
    if (days === 0) return 'Today';
    if (days === 1) return 'Tomorrow';
    return `${days} days`;
  };

  const daysUntilDeadline = getDaysUntilDeadline(scheme.deadline);
  const deadlineColor = getDeadlineColor(daysUntilDeadline);
  const deadlineText = getDeadlineText(daysUntilDeadline);

  return (
    <Card className="border-l-4 border-l-blue-500">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-stone-900">{scheme.name}</h3>
        <p className="text-sm text-stone-600 mt-1">{scheme.ministry}</p>
      </div>

      <div className="space-y-4">
        {/* Benefit Amount */}
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-700">
            {scheme.benefit}
          </div>
          <div className="text-sm text-green-600 mt-1">Maximum Benefit</div>
        </div>

        {/* Deadline */}
        {scheme.deadline && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-stone-700">Application Deadline:</span>
            <Badge variant={deadlineColor}>
              {deadlineText}
            </Badge>
          </div>
        )}

        {/* Eligibility */}
        <div>
          <span className="text-sm font-medium text-stone-700">Eligibility Criteria:</span>
          <ul className="mt-2 space-y-1">
            {scheme.eligibility.map((item, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-stone-600">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Description */}
        <div className="p-3 bg-stone-50 rounded-lg">
          <p className="text-sm text-stone-700">{scheme.description}</p>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <Button variant="outline" size="sm">
            Check Eligibility
          </Button>
          <Button variant="primary" size="sm" icon={ExternalLink}>
            Apply Now
          </Button>
        </div>

        {/* Additional Info */}
        <div className="text-xs text-stone-500 border-t border-stone-200 pt-3">
          <div className="flex items-center gap-2">
            <Calendar className="w-3 h-3" />
            <span>Last updated: {new Date().toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export { SchemeCard };
