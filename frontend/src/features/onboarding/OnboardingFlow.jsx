import React, { useState } from 'react';
import { LanguageSelect } from './components/LanguageSelect';
import { LocationPermission } from './components/LocationPermission';
import { CropSetup } from './components/CropSetup';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { useFieldStore } from '../../stores/useFieldStore.jsx';

const OnboardingFlow = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [onboardingData, setOnboardingData] = useState({
    language: 'en',
    location: null,
    crops: [],
    fieldSize: null,
    areaUnit: 'acres',
  });

  const { completeOnboarding } = useUserStore();
  const { addField } = useFieldStore();

  const steps = [
    {
      component: LanguageSelect,
      title: 'Language Selection',
    },
    {
      component: LocationPermission,
      title: 'Location Permission',
    },
    {
      component: CropSetup,
      title: 'Crop Setup',
    },
  ];

  const CurrentStepComponent = steps[currentStep].component;

  const handleLanguageSelect = (language) => {
    setOnboardingData(prev => ({ ...prev, language }));
  };

  const handleLocationSet = (location) => {
    setOnboardingData(prev => ({ ...prev, location }));
  };

  const handleCropSetup = (cropData) => {
    setOnboardingData(prev => ({ ...prev, ...cropData }));
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    // Create user profile
    const userProfile = {
      name: 'Farmer', // Default name, can be updated later
      village: onboardingData.location?.village || 'Unknown',
      state: onboardingData.location?.state || 'Unknown',
      language: onboardingData.language,
    };

    // Complete onboarding
    completeOnboarding(userProfile);

    // Create initial field if crops and field size provided
    if (onboardingData.crops.length > 0 && onboardingData.fieldSize) {
      addField({
        name: 'Main Field',
        crop: onboardingData.crops[0], // Primary crop
        area: onboardingData.fieldSize,
        areaUnit: onboardingData.areaUnit,
        soilType: 'Loamy', // Default
        location: onboardingData.location || {
          village: userProfile.village,
          district: '',
          state: userProfile.state,
        },
      });
    }

    // Call completion callback
    onComplete();
  };

  return (
    <CurrentStepComponent
      selectedLanguage={onboardingData.language}
      onLanguageSelect={handleLanguageSelect}
      onLocationSet={handleLocationSet}
      onCropSetup={handleCropSetup}
      onNext={handleNext}
      onBack={handleBack}
    />
  );
};

export { OnboardingFlow };
