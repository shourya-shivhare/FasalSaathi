import React, { useState } from 'react';
import { TopBar } from '../../components/layout/TopBar';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { MessageList } from './components/MessageList';
import { AgentThinkingAccordion } from './components/AgentThinkingAccordion';
import { QuickReplySuggestions } from './components/QuickReplySuggestions';
import { ChatInput } from './components/ChatInput';
import { useChatStore } from '../../stores/useChatStore.jsx';

const ChatPage = () => {
  const {
    messages,
    isThinking,
    agentSteps,
    suggestions,
    isListening,
    sendMessage,
    setListening,
  } = useChatStore();

  const handleSendMessage = (text) => {
    sendMessage(text);
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  const handleToggleListening = () => {
    // In a real app, this would integrate with Web Speech API
    setListening(!isListening);
    
    // Simulate voice input after 2 seconds
    if (!isListening) {
      setTimeout(() => {
        const simulatedVoiceInput = 'What fertilizer should I use for my wheat crop?';
        sendMessage(simulatedVoiceInput);
        setListening(false);
      }, 2000);
    }
  };

  return (
    <PageWrapper className="flex flex-col">
      <TopBar
        title="FasalSaathi Chat"
        subtitle="Your AI farming assistant"
        showBack={false}
      />

      <div className="flex-1 flex flex-col pt-14">
        <MessageList messages={messages} isThinking={isThinking} />
        
        <AgentThinkingAccordion 
          agentSteps={agentSteps} 
          isThinking={isThinking} 
        />
        
        <QuickReplySuggestions
          suggestions={suggestions}
          onSuggestionClick={handleSuggestionClick}
        />
        
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isThinking}
          isListening={isListening}
          onToggleListening={handleToggleListening}
        />
      </div>
    </PageWrapper>
  );
};

export { ChatPage };
