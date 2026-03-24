import React from 'react';
import { MessageList } from './components/MessageList';
import { AgentThinkingAccordion, ChatHeader } from './components/ChatHeader';
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

  const handleSendMessage = (text) => sendMessage(text);

  const handleSuggestionClick = (suggestion) => sendMessage(suggestion);

  const handleToggleListening = () => {
    setListening(!isListening);
    if (!isListening) {
      setTimeout(() => {
        sendMessage('What fertilizer should I use for my wheat crop?');
        setListening(false);
      }, 2000);
    }
  };

  return (
    /*
     * Full-height column layout:
     *  ┌─ ChatHeader (fixed 60px) ────────────────────────┐
     *  │  MessageList (flex-1, scrollable)                 │
     *  │  AgentThinkingAccordion (shows when thinking)     │
     *  │  QuickReplySuggestions (horizontal chips)         │
     *  └─ ChatInput (sticky bottom) ──────────────────────┘
     */
    <div
      className="flex flex-col"
      style={{
        /* subtract bottom-nav height (64px) so input is never hidden */
        height: 'calc(100dvh - 64px)',
        maxHeight: 'calc(100dvh - 64px)',
        background: '#f0fdf4',
      }}
    >
      {/* Green WhatsApp-style header */}
      <ChatHeader isThinking={isThinking} />

      {/* Scrollable message window — padded under fixed header */}
      <div
        className="flex flex-col flex-1 overflow-hidden"
        style={{ paddingTop: '60px' }}
      >
        <MessageList messages={messages} isThinking={isThinking} />

        {/* Thinking accordion floats above the input */}
        <AgentThinkingAccordion agentSteps={agentSteps} isThinking={isThinking} />

        {/* Quick reply chips */}
        <QuickReplySuggestions
          suggestions={suggestions}
          onSuggestionClick={handleSuggestionClick}
        />

        {/* Input bar */}
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isThinking}
          isListening={isListening}
          onToggleListening={handleToggleListening}
        />
      </div>
    </div>
  );
};

export { ChatPage };
