import React from 'react';
import { Globe } from 'lucide-react';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { Button } from '../ui/Button';

const LanguageToggle = () => {
  const { language, setLanguage } = useUserStore();

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'hi' : 'en');
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleLanguage}
      icon={Globe}
      className="text-stone-600"
    >
      {language === 'en' ? 'EN' : 'हिं'}
    </Button>
  );
};

export { LanguageToggle };
