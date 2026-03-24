import { useEffect, useRef } from 'react';

export const useChatScroll = (messages, isThinking) => {
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  return {
    messagesEndRef,
    containerRef,
    scrollToBottom,
  };
};
