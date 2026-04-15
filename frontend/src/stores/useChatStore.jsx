// src/stores/useChatStore.jsx
// Connects to the real FasalSaathi AI service via the backend proxy.
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// ── helpers ─────────────────────────────────────────────────────────────────
function getAccessToken() {
  try {
    const raw = localStorage.getItem('fasalsaathi-user');
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed?.state?.accessToken || null;
  } catch { return null; }
}

// ── session ID persisted across page refreshes ─────────────────────────────
function getOrCreateSessionId() {
  let sid = localStorage.getItem('fasalsaathi_session_id');
  if (!sid) {
    sid = `sess-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem('fasalsaathi_session_id', sid);
  }
  return sid;
}

export const useChatStore = create(
  persist(
    (set, get) => ({
  messages: [],          // { role: 'user'|'assistant', content: string, id: string }
  isThinking: false,
  isListening: false,
  sessionId: getOrCreateSessionId(),
  analysisContext: null, // Orchestrator output: { crops, schemes, summary }

  // ── Set analysis context from orchestrator pipeline output ────────────────
  setAnalysisContext: (pipelineResponse) => {
    if (!pipelineResponse) return set({ analysisContext: null });
    set((state) => {
      const existing = state.analysisContext || {};
      return {
        analysisContext: {
          crops: pipelineResponse.crop_recommendations !== undefined ? pipelineResponse.crop_recommendations : existing.crops,
          schemes: pipelineResponse.scheme_recommendations !== undefined ? pipelineResponse.scheme_recommendations : existing.schemes,
          summary: pipelineResponse.summary !== undefined ? pipelineResponse.summary : existing.summary,
        }
      };
    });
  },

  // ── Send a message and await the AI response ─────────────────────────────
  sendMessage: async (text) => {
    if (!text?.trim()) return;

    const userMsg = { id: `u-${Date.now()}`, role: 'user', content: text };
    set((state) => ({ messages: [...state.messages, userMsg], isThinking: true }));

    try {
      const { messages, sessionId } = get();

      // Build the messages array for the API — all messages including the new one
      const apiMessages = messages.map((m) => ({ role: m.role, content: m.content }));

      const isAnalyze = text.toLowerCase().startsWith('/analyze');
      const token = getAccessToken();
      let answer;

      if (isAnalyze) {
        // Reroute exclusively to the Agent Orchestrator and Planner
        const actualQuery = text.replace(/^\/analyze\s*/i, '');
        let farmer = {};
        try {
           farmer = JSON.parse(localStorage.getItem('fasalsaathi-user'))?.state?.farmerProfile || {};
        } catch {}

        const payload = {
           user_query: actualQuery || 'Full analysis please',
           state: farmer.state || 'Unknown',
           district: farmer.district || '',
           farmer_category: farmer.farmer_category || 'marginal',
           season: farmer.season || 'Rabi',
           soil_type: farmer.soil_type || 'Loamy',
           previous_analysis_context: get().analysisContext || {}
        };
        const res = await fetch(`${API_BASE}/agents/full-analysis`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        
        // Output the orchestrator summary into chat!
        answer = `*Orchestrator Analysis Complete!*\n\n${data.summary}\n\n*Agents Chosen:* ${data.steps[0].data.agents_selected.join(', ')}`;
        
        // Persist the context
        get().setAnalysisContext(data);
      } else {
        // Standard LangGraph Chat Pipeline
        const res = await fetch(`${API_BASE}/chat/`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          body: JSON.stringify({
            messages: apiMessages,
            session_id: sessionId,
            ...(get().analysisContext ? { analysis_context: get().analysisContext } : {}),
          }),
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        answer = data.answer || 'Maafi chahta hoon, abhi jawab dene mein dikkat aa rahi hai.';

        // Update session ID if the server returned a new one
        if (data.session_id && data.session_id !== sessionId) {
          localStorage.setItem('fasalsaathi_session_id', data.session_id);
          set({ sessionId: data.session_id });
        }
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
    // Extract pest names from results array (each item has .pest or .class)
    const pestNames = (scanData.results || [])
      .map((r) => r.pest || r.class || 'Unknown')
      .filter(Boolean);
    const pestName = pestNames.length > 0 ? pestNames.join(', ') : 'Unknown Pest';

    // Build detailed detection info for richer context
    const detectionDetails = (scanData.results || [])
      .map((r) => {
        const name = r.pest || r.class || 'Unknown';
        const conf = r.confidence ? `${Math.round(r.confidence * 100)}%` : 'N/A';
        const sev = r.severity || 'Medium';
        return `${name} (Confidence: ${conf}, Severity: ${sev})`;
      })
      .join('; ');

    const suggestions = scanData.suggestions?.join('. ') || 'No suggestions available.';
    
    const secretMsg = {
      id: `u-${Date.now()}-hidden`,
      role: 'user',
      content: `[SYSTEM: SECRET CONTEXT. DO NOT MENTION THAT I TOLD YOU THIS OR THAT YOU RECEIVED A SYSTEM MESSAGE. The user just uploaded an image of their crop. The AI pest detection system analyzed it and found: ${detectionDetails || pestName}. Total pests detected: ${scanData.total || pestNames.length}. The suggested treatments are: ${suggestions}. Please give a warm, supportive greeting as FasalSaathi AI. Acknowledge the exact pest found in their crop, briefly summarize the treatments you recommend, and ask if they have any specific questions about applying these treatments or anything else.]`,
      isHidden: true
    };

    // Start a fresh session for this scan handoff
    const newSid = `sess-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem('fasalsaathi_session_id', newSid);
    set({ messages: [secretMsg], isThinking: true, sessionId: newSid });

    try {
      const { messages, sessionId } = get();
      const apiMessages = messages.map((m) => ({ role: m.role, content: m.content }));

      const token = getAccessToken();
      const res = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
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
      // Show a helpful fallback so the user isn't stuck on an empty chat
      const fallbackMsg = {
        id: `a-${Date.now()}`,
        role: 'assistant',
        content: `🌾 **Pest Detection Summary**\n\n${pestName} detected in your crop.\n\n**Suggested Treatment:**\n${suggestions}\n\n⚠️ AI expert is currently unavailable (quota limit reached). You can ask follow-up questions once the service is back online.`,
      };
      set((state) => ({
        messages: [...state.messages, fallbackMsg],
        isThinking: false,
      }));
    }
  },

  // ── Clear conversation (new chat) ─────────────────────────────────────────
  clearChat: () => {
    const newSid = `sess-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem('fasalsaathi_session_id', newSid);
    set({ messages: [], isThinking: false, sessionId: newSid, analysisContext: null });
  },

  // ── Voice listening toggle ────────────────────────────────────────────────
  setListening: (isListening) => set({ isListening }),
}),
    {
      name: 'fasalsaathi-chat',
      partialize: (s) => ({
        messages: s.messages,
        sessionId: s.sessionId,
        analysisContext: s.analysisContext,
      }),
    }
  )
);
