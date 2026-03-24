import React from 'react';
import { Button } from '../../../components/ui/Button';

const LanguageSelect = ({ selectedLanguage, onLanguageSelect, onNext }) => {
  const languages = [
    { code: 'hi', name: 'हिंदी', label: 'Hindi' },
    { code: 'en', name: 'English', label: 'English' },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 bg-stone-50">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="text-6xl mb-4">🌾</div>
          <h1 className="text-2xl font-bold text-stone-900 mb-2">
            अपनी भाषा चुनें / Choose your language
          </h1>
          <p className="text-stone-600">
            Select your preferred language to continue
          </p>
        </div>

        {/* Language Options */}
        <div className="space-y-4">
          {languages.map((language) => (
            <Button
              key={language.code}
              variant={selectedLanguage === language.code ? 'primary' : 'outline'}
              size="lg"
              fullWidth
              onClick={() => {
                onLanguageSelect(language.code);
                onNext();
              }}
              className={`h-16 text-lg ${
                selectedLanguage === language.code
                  ? 'bg-brand-600 hover:bg-brand-700'
                  : 'bg-white hover:bg-stone-50'
              }`}
            >
              <div className="flex items-center justify-center gap-3">
                <span className="text-2xl">{language.name}</span>
                <span className="text-stone-500">•</span>
                <span className="text-stone-600">{language.label}</span>
              </div>
            </Button>
          ))}
        </div>

        {/* Progress Indicator */}
        <div className="flex justify-center gap-2">
          <div className="w-8 h-2 bg-brand-600 rounded-full" />
          <div className="w-8 h-2 bg-stone-300 rounded-full" />
          <div className="w-8 h-2 bg-stone-300 rounded-full" />
        </div>

        {/* Skip Option */}
        <div className="text-center">
          <button
            onClick={() => onNext()}
            className="text-stone-500 hover:text-stone-700 text-sm underline"
          >
            Continue with English →
          </button>
        </div>
      </div>
    </div>
  );
};

export { LanguageSelect };
