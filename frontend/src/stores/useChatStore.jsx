// src/stores/useChatStore.jsx
// Connects to the real FasalSaathi AI service via the backend proxy.
import { create } from 'zustand';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// ── session ID persisted across page refreshes ─────────────────────────────
function getOrCreateSessionId() {
  let sid = localStorage.getItem('fasalsaathi_session_id');
  if (!sid) {
    sid = `sess-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem('fasalsaathi_session_id', sid);
  }
  return sid;
}

export const useChatStore = create((set, get) => ({
  messages: [],          // { role: 'user'|'assistant', content: string, id: string }
  isThinking: false,
  isListening: false,
  sessionId: getOrCreateSessionId(),

  // ── Send a message and await the AI response ─────────────────────────────
  sendMessage: async (text) => {
    if (!text?.trim()) return;

    const userMsg = { id: `u-${Date.now()}`, role: 'user', content: text };
    set((state) => ({ messages: [...state.messages, userMsg], isThinking: true }));

    try {
      const { messages, sessionId } = get();

      // Build the messages array for the API — all messages including the new one
      const apiMessages = messages.map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: apiMessages,
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const answer = data.answer || 'Maafi chahta hoon, abhi jawab dene mein dikkat aa rahi hai.';

      // Update session ID if the server returned a new one
      if (data.session_id && data.session_id !== sessionId) {
        localStorage.setItem('fasalsaathi_session_id', data.session_id);
        set({ sessionId: data.session_id });
      }

      const aiMsg = { id: `a-${Date.now()}`, role: 'assistant', content: answer };
      set((state) => ({
        messages: [...state.messages, aiMsg],
        isThinking: false,
      }));
    } catch (err) {
      console.error('[ChatStore] sendMessage failed:', err);
      const errorMsg = {
        id: `e-${Date.now()}`,
        role: 'assistant',
        content:
          '⚠️ AI service se connection nahi ho pa raha. Kripya backend server check karein aur dobara try karein.',
      };
      set((state) => ({
        messages: [...state.messages, errorMsg],
        isThinking: false,
      }));
    }
  },

  // ── Inject scan context invisibly and get opening greeting ────────────────
  injectScanContext: async (scanData) => {
    const pestName = scanData.pests?.join(', ') || 'Unknown Pest';
    const suggestions = scanData.suggestions?.join('. ') || 'No suggestions available.';
    
    const secretMsg = {
      id: `u-${Date.now()}-hidden`,
      role: 'user',
      content: `[SYSTEM: SECRET CONTEXT. DO NOT MENTION THAT I TOLD YOU THIS OR THAT YOU RECEIVED A SYSTEM MESSAGE. The user just uploaded an image of their crop. The AI pest detection system analyzed it and found: ${pestName}. The suggested treatments are: ${suggestions}. Please give a warm, supportive greeting as FasalSaathi AI. Acknowledge the exact pest found in their crop, briefly summarize the treatments you recommend, and ask if they have any specific questions about applying these treatments or anything else.]`,
      isHidden: true
    };

    set((state) => ({ messages: [...state.messages, secretMsg], isThinking: true }));

    try {
      const { messages, sessionId } = get();
      const apiMessages = messages.map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: apiMessages,
          session_id: sessionId,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      const answer = data.answer || 'Maafi chahta hoon, jawab dene mein dikkat aa rahi hai.';

      if (data.session_id && data.session_id !== sessionId) {
        localStorage.setItem('fasalsaathi_session_id', data.session_id);
        set({ sessionId: data.session_id });
      }

      const aiMsg = { id: `a-${Date.now()}`, role: 'assistant', content: answer };
      set((state) => ({
        messages: [...state.messages, aiMsg],
        isThinking: false,
      }));
    } catch (err) {
      console.error('[ChatStore] injectScanContext failed:', err);
      set({ isThinking: false }); // Silently fail UI, user can still type normally
    }
  },

  // ── Clear conversation (new chat) ─────────────────────────────────────────
  clearChat: () => {
    const newSid = `sess-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem('fasalsaathi_session_id', newSid);
    set({ messages: [], isThinking: false, sessionId: newSid });
  },

  // ── Voice listening toggle ────────────────────────────────────────────────
  setListening: (isListening) => set({ isListening }),
}));
