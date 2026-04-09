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

  // ── Clear conversation (new chat) ─────────────────────────────────────────
  clearChat: () => {
    const newSid = `sess-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem('fasalsaathi_session_id', newSid);
    set({ messages: [], isThinking: false, sessionId: newSid });
  },

  // ── Voice listening toggle ────────────────────────────────────────────────
  setListening: (isListening) => set({ isListening }),
}));
