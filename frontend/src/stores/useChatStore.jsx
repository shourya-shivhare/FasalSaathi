import { create } from 'zustand';
import { mockChatMessages, mockAgentSteps } from '../lib/mockData';

export const useChatStore = create((set, get) => ({
  messages: mockChatMessages,
  isThinking: false,
  agentSteps: mockAgentSteps,
  suggestions: [
    'What fertilizer should I use?',
    'Show weather forecast',
    'Nearest Krishi Kendra',
    "Today's mandi prices",
  ],
  isListening: false,

  sendMessage: async (text) => {
    const userMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      text,
      timestamp: new Date(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isThinking: true,
      agentSteps: state.agentSteps.map((step) => ({
        ...step,
        status: 'pending',
      })),
    }));

    // Simulate agent thinking process
    setTimeout(() => {
      get().appendAgentStep({
        id: 'step-1',
        label: 'Analyzing query',
        status: 'done',
        detail: 'Understanding your question',
      });
    }, 1000);

    setTimeout(() => {
      get().appendAgentStep({
        id: 'step-2',
        label: 'Checking field data',
        status: 'done',
        detail: 'Retrieving relevant information',
      });
    }, 2000);

    setTimeout(() => {
      get().appendAgentStep({
        id: 'step-3',
        label: 'Generating response',
        status: 'done',
        detail: 'Preparing recommendations',
      });
    }, 3000);

    // Simulate agent response
    setTimeout(() => {
      const agentMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'agent',
        text: 'I understand your question. Based on your field data and current conditions, here are my recommendations...',
        timestamp: new Date(),
      };

      set((state) => ({
        messages: [...state.messages, agentMessage],
        isThinking: false,
        suggestions: [
          'Tell me more about this',
          'What should I do next?',
          'Show me field details',
          'Check weather impact',
        ],
      }));
    }, 4000);
  },

  appendAgentStep: (step) => {
    set((state) => ({
      agentSteps: state.agentSteps.map((s) =>
        s.id === step.id ? { ...s, ...step } : s
      ),
    }));
  },

  resolveStep: (stepId) => {
    set((state) => ({
      agentSteps: state.agentSteps.map((step) =>
        step.id === stepId ? { ...step, status: 'done' } : step
      ),
    }));
  },

  setThinking: (isThinking) => {
    set({ isThinking });
  },

  addAgentMessage: ({ text, actionCard }) => {
    const message = {
      id: `msg-${Date.now()}`,
      role: 'agent',
      text,
      timestamp: new Date(),
      ...(actionCard && { actionCard }),
    };

    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  clearChat: () => {
    set({
      messages: [],
      agentSteps: [],
      isThinking: false,
    });
  },

  setListening: (isListening) => {
    set({ isListening });
  },
}));
