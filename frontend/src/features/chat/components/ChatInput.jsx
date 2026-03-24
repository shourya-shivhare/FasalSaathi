import React, { useState, useRef } from 'react';
import { Send, Mic, MicOff } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';

const ChatInput = ({ onSendMessage, disabled = false, isListening = false, onToggleListening }) => {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput('');
      inputRef.current?.focus();
    }
  };

  const handleVoiceToggle = () => {
    onToggleListening();
  };

  return (
    <div className="border-t border-stone-200 bg-white p-4">
      {/* Listening Overlay */}
      {isListening && (
        <div className="absolute inset-x-0 top-0 bg-red-50 border-b border-red-200 p-2 text-center">
          <div className="flex items-center justify-center gap-2 text-red-600">
            <MicOff className="w-4 h-4 animate-pulse" />
            <span className="text-sm font-medium">Listening...</span>
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask FasalSaathi..."
            disabled={disabled || isListening}
            className="w-full px-4 py-3 bg-stone-50 border border-stone-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed text-base"
          />
        </div>
        
        <Button
          type="button"
          variant={isListening ? 'danger' : 'ghost'}
          size="md"
          onClick={handleVoiceToggle}
          disabled={disabled}
          className={`flex-shrink-0 ${isListening ? 'animate-pulse bg-red-600 text-white' : 'text-stone-600'}`}
        >
          {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </Button>
        
        <Button
          type="submit"
          variant="primary"
          size="md"
          disabled={disabled || !input.trim() || isListening}
          className="flex-shrink-0"
        >
          <Send className="w-5 h-5" />
        </Button>
      </form>
    </div>
  );
};

export { ChatInput };
