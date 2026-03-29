import React from 'react';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { ProgressBar } from '../../../components/ui/ProgressBar';
import { GROWTH_STAGES } from '../../../lib/constants.jsx';

const CropStatusBanner = ({ field }) => {
  const getCropEmoji = (crop) => {
    const cropEmojis = {
      Wheat: '🌾',
      Rice: '🌾',
      Cotton: '🌱',
      Soybean: '🫘',
      Maize: '🌽',
    };
    return cropEmojis[crop] || '🌱';
  };

  const getCurrentStageIndex = (currentStage) => {
    return GROWTH_STAGES.findIndex(stage => 
      stage.toLowerCase().includes(currentStage.toLowerCase()) ||
      currentStage.toLowerCase().includes(stage.toLowerCase())
    );
  };

  const getDaysToHarvest = (growthStage) => {
    const daysMap = {
      'Sowing': 120,
      'Germination': 100,
      'Vegetative': 60,
      'Flowering': 30,
      'Tillering Stage': 80,
      'Harvest': 0,
    };
    return daysMap[growthStage] || 60;
  };

  const getProgressPercentage = (currentStage) => {
    const currentIndex = getCurrentStageIndex(currentStage);
    return currentIndex >= 0 ? ((currentIndex + 1) / GROWTH_STAGES.length) * 100 : 20;
  };

  return (
    <Card highlighted className="transition-all duration-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getCropEmoji(field.crop)}</span>
          <div>
            <h3 className="text-lg font-semibold theme-text-primary transition-colors duration-200">
              {field.crop}
            </h3>
            <Badge variant="info" className="mt-1">
              {field.growthStage}
            </Badge>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-2xl font-bold theme-text-accent-primary transition-colors duration-200">
            {getDaysToHarvest(field.growthStage)}
          </div>
          <div className="text-xs theme-text-secondary opacity-80 transition-colors duration-200">days to harvest</div>
        </div>
      </div>

      <div>
        <div className="flex justify-between text-xs theme-text-secondary mb-2 transition-colors duration-200">
          <span>Growth Progress</span>
          <span className="font-medium theme-text-primary">{Math.round(getProgressPercentage(field.growthStage))}%</span>
        </div>
        
        <ProgressBar
          value={getProgressPercentage(field.growthStage)}
          colorScheme="green"
          className="mb-3"
        />

        <div className="flex justify-between text-[10px] sm:text-xs">
          {GROWTH_STAGES.map((stage, index) => {
            const currentIndex = getCurrentStageIndex(field.growthStage);
            const isCompleted = index < currentIndex;
            const isCurrent = index === currentIndex;
            
            return (
              <div
                key={stage}
                className={`flex flex-col items-center flex-1 ${
                  isCompleted ? 'theme-text-success' : isCurrent ? 'theme-text-accent-primary' : 'theme-text-secondary'
                } transition-colors duration-200`}
              >
                <div
                  className={`w-2 h-2 rounded-full mb-1 ${
                    isCompleted ? 'theme-bg-success' : isCurrent ? 'theme-bg-accent-primary' : 'theme-bg-surface-hover'
                  } transition-colors duration-200`}
                />
                <span className="max-w-[50px] text-center leading-tight opacity-90">
                  {stage}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};

export { CropStatusBanner };
