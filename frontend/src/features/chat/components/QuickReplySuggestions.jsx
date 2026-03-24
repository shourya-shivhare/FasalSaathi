import React from 'react';
import { Button } from '../../../components/ui/Button';

const QuickReplySuggestions = ({ suggestions, onSuggestionClick }) => {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="px-4 pb-4">
      <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
        {suggestions.map((suggestion, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onSuggestionClick(suggestion)}
            className="flex-shrink-0 whitespace-nowrap"
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
};

export { QuickReplySuggestions };
