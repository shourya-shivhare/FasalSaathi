import React from 'react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';

const CropCalendar = ({ crop, growthStage, plantingDate }) => {
  // Generate calendar timeline based on crop and current stage
  const generateTimeline = () => {
    const stages = [
      { name: 'Sowing', start: 0, duration: 7, color: 'bg-green-500', type: 'window' },
      { name: 'Germination', start: 7, duration: 14, color: 'bg-green-400', type: 'stage' },
      { name: 'Vegetative', start: 21, duration: 35, color: 'bg-amber-500', type: 'stage' },
      { name: 'Fertilizer 1', start: 28, duration: 1, color: 'bg-amber-600', type: 'fertilizer' },
      { name: 'Fertilizer 2', start: 42, duration: 1, color: 'bg-amber-600', type: 'fertilizer' },
      { name: 'Irrigation 1', start: 21, duration: 1, color: 'bg-blue-500', type: 'irrigation' },
      { name: 'Irrigation 2', start: 35, duration: 1, color: 'bg-blue-500', type: 'irrigation' },
      { name: 'Irrigation 3', start: 49, duration: 1, color: 'bg-blue-500', type: 'irrigation' },
      { name: 'Flowering', start: 56, duration: 21, color: 'bg-purple-500', type: 'stage' },
      { name: 'Harvest', start: 77, duration: 14, color: 'bg-yellow-500', type: 'window' },
    ];

    // Calculate current day based on planting date
    const plantingDateObj = new Date(plantingDate);
    const currentDate = new Date();
    const currentDay = Math.floor((currentDate - plantingDateObj) / (1000 * 60 * 60 * 24));

    return { stages, currentDay };
  };

  const { stages, currentDay } = generateTimeline();
  const totalDays = 120; // Typical crop duration

  const getMonthDay = (day) => {
    const date = new Date(plantingDate);
    date.setDate(date.getDate() + day);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getStagePosition = (start, duration) => {
    const left = (start / totalDays) * 100;
    const width = (duration / totalDays) * 100;
    return { left: `${left}%`, width: `${width}%` };
  };

  const isCurrentStage = (stage) => {
    return currentDay >= stage.start && currentDay < stage.start + stage.duration;
  };

  const isPastStage = (stage) => {
    return currentDay >= stage.start + stage.duration;
  };

  return (
    <Card>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-stone-900">Crop Calendar</h3>
        <p className="text-sm text-stone-600 mt-1">
          {crop} growth timeline and important dates
        </p>
      </div>

      {/* Current Status */}
      <div className="mb-6 p-3 bg-stone-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm text-stone-600">Current Stage:</span>
            <div className="font-medium text-stone-900">{growthStage}</div>
          </div>
          <div className="text-right">
            <span className="text-sm text-stone-600">Day {currentDay} of {totalDays}</span>
            <div className="w-32 bg-stone-200 rounded-full h-2 mt-1">
              <div
                className="bg-brand-500 h-2 rounded-full"
                style={{ width: `${(currentDay / totalDays) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Month markers */}
        <div className="flex justify-between text-xs text-stone-500 mb-2">
          <span>{getMonthDay(0)}</span>
          <span>{getMonthDay(30)}</span>
          <span>{getMonthDay(60)}</span>
          <span>{getMonthDay(90)}</span>
          <span>{getMonthDay(120)}</span>
        </div>

        {/* Timeline bar */}
        <div className="relative h-12 bg-stone-100 rounded-lg overflow-hidden">
          {/* Growth stages */}
          {stages
            .filter(stage => stage.type === 'stage' || stage.type === 'window')
            .map((stage) => {
              const position = getStagePosition(stage.start, stage.duration);
              const isCurrent = isCurrentStage(stage);
              const isPast = isPastStage(stage);
              
              return (
                <div
                  key={stage.name}
                  className={`absolute top-2 h-8 ${stage.color} ${
                    isCurrent ? 'ring-2 ring-offset-1 ring-brand-500' : ''
                  } ${isPast ? 'opacity-60' : ''} rounded`}
                  style={position}
                >
                  <div className="text-xs text-white font-medium text-center leading-8">
                    {stage.name}
                  </div>
                </div>
              );
            })}

          {/* Fertilizer markers */}
          {stages
            .filter(stage => stage.type === 'fertilizer')
            .map((stage) => {
              const position = (stage.start / totalDays) * 100;
              const isCurrent = isCurrentStage(stage);
              const isPast = isPastStage(stage);
              
              return (
                <div
                  key={stage.name}
                  className={`absolute top-0 w-2 h-12 ${stage.color} ${
                    isCurrent ? 'ring-2 ring-offset-1 ring-amber-500' : ''
                  } ${isPast ? 'opacity-60' : ''}`}
                  style={{ left: `${position}%` }}
                  title={stage.name}
                />
              );
            })}

          {/* Irrigation markers */}
          {stages
            .filter(stage => stage.type === 'irrigation')
            .map((stage) => {
              const position = (stage.start / totalDays) * 100;
              const isCurrent = isCurrentStage(stage);
              const isPast = isPastStage(stage);
              
              return (
                <div
                  key={stage.name}
                  className={`absolute top-0 w-2 h-12 ${stage.color} ${
                    isCurrent ? 'ring-2 ring-offset-1 ring-blue-500' : ''
                  } ${isPast ? 'opacity-60' : ''}`}
                  style={{ left: `${position}%` }}
                  title={stage.name}
                />
              );
            })}

          {/* Current day indicator */}
          <div
            className="absolute top-0 w-0.5 h-12 bg-red-500"
            style={{ left: `${(currentDay / totalDays) * 100}%` }}
          >
            <div className="absolute -top-1 -left-1 w-2 h-2 bg-red-500 rounded-full" />
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-3 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-amber-600 rounded" />
          <span className="text-stone-600">Fertilizer</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-blue-500 rounded" />
          <span className="text-stone-600">Irrigation</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-green-500 rounded" />
          <span className="text-stone-600">Sowing Window</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-yellow-500 rounded" />
          <span className="text-stone-600">Harvest Window</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-500 rounded" />
          <span className="text-stone-600">Today</span>
        </div>
      </div>

      {/* Upcoming Activities */}
      <div className="mt-4">
        <h4 className="text-sm font-medium text-stone-900 mb-2">Upcoming Activities</h4>
        <div className="space-y-2">
          {stages
            .filter(stage => stage.start > currentDay && stage.start <= currentDay + 14)
            .slice(0, 3)
            .map((stage) => (
              <div key={stage.name} className="flex items-center justify-between p-2 bg-stone-50 rounded">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 ${stage.color} rounded`} />
                  <span className="text-sm text-stone-700">{stage.name}</span>
                </div>
                <span className="text-xs text-stone-500">
                  Day {stage.start} ({getMonthDay(stage.start)})
                </span>
              </div>
            ))}
        </div>
      </div>
    </Card>
  );
};

export { CropCalendar };
