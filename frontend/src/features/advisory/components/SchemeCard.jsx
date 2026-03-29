import React from 'react';
import { Calendar, ExternalLink, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';

const SchemeCard = ({ scheme, isExpanded, onToggle }) => {
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
    <Card 
      className={`border-l-4 border-l-blue-500 transition-all duration-300 cursor-pointer ${isExpanded ? 'shadow-lg ring-1 ring-blue-500/20' : 'hover:shadow-md active:scale-[0.99]'}`}
      onClick={onToggle}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1 pr-4">
          <h3 className="text-lg font-bold theme-text-primary leading-tight">{scheme.name}</h3>
          <p className="text-xs theme-text-secondary mt-1 font-medium">{scheme.ministry}</p>
        </div>
        <div className="p-1 rounded-full theme-bg-surface-hover transition-colors flex-shrink-0">
          {isExpanded ? <ChevronUp className="w-5 h-5 theme-text-secondary" /> : <ChevronDown className="w-5 h-5 theme-text-secondary" />}
        </div>
      </div>

      <div className={`overflow-hidden transition-all duration-300 ${isExpanded ? 'max-h-[1000px] opacity-100 mt-4' : 'max-h-12 opacity-80'}`}>
        <p className={`text-sm theme-text-secondary leading-relaxed ${!isExpanded && 'line-clamp-2'}`}>
          {scheme.description}
        </p>
      </div>

      {!isExpanded && (
        <div className="mt-3 flex items-center justify-between">
          <span className="text-[10px] font-bold theme-text-accent-primary uppercase tracking-wider">Click to read more</span>
          {scheme.deadline && <Badge variant={deadlineColor} size="sm">{deadlineText}</Badge>}
        </div>
      )}

      {isExpanded && (
        <div className="mt-6 space-y-6 animate-in fade-in slide-in-from-top-2 duration-300">
          {/* Benefit Amount */}
          <div className="text-center p-4 theme-bg-surface-hover rounded-2xl border theme-border">
            <div className="text-2xl font-black theme-text-success">
              {scheme.benefit}
            </div>
            <div className="text-xs font-bold theme-text-secondary mt-1 uppercase tracking-widest">Maximum Benefit</div>
          </div>

          {/* Deadline info */}
          <div className="flex items-center justify-between px-1">
            <span className="text-sm font-bold theme-text-primary">Status:</span>
            <Badge variant={deadlineColor}>
              {deadlineText}
            </Badge>
          </div>

          {/* Eligibility */}
          <div className="space-y-3">
            <span className="text-sm font-bold theme-text-primary px-1">Eligibility Criteria:</span>
            <ul className="space-y-2">
              {scheme.eligibility.map((item, index) => (
                <li key={index} className="flex items-start gap-3 text-sm theme-text-secondary bg-theme-bg-secondary/30 p-3 rounded-xl border theme-border">
                  <CheckCircle className="w-4 h-4 text-theme-success mt-0.5 flex-shrink-0" />
                  <span className="leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-4 pt-2">
            <Button variant="outline" size="md">
              Check Status
            </Button>
            <Button variant="primary" size="md" icon={ExternalLink}>
              Apply Now
            </Button>
          </div>

          {/* Additional Info */}
          <div className="text-[10px] theme-text-secondary border-t theme-border pt-4 flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <Calendar className="w-3 h-3" />
              <span>Last updated: {new Date().toLocaleDateString()}</span>
            </div>
            <span className="font-bold theme-text-accent-primary uppercase tracking-tighter">Verified Official</span>
          </div>
        </div>
      )}
    </Card>
  );
};

export { SchemeCard };
