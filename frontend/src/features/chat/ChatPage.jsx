import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, Mic, MicOff, Leaf, Sparkles } from 'lucide-react';
import { useChatStore } from '../../stores/useChatStore.jsx';

const suggestions = [
  'Market prices today?',
  'Kab paani daalna chahiye?',
  'Spray schedule kya hoga?',
  'Subsidy info chahiye',
  'Wheat ke liye fertilizer',
];

const ChatPage = () => {
  const { messages, isThinking, sendMessage, isListening, setListening } = useChatStore();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || isThinking) return;
    sendMessage(text);
    setInput('');
  };

  const handleKey = (e) => { 
    if (e.key === 'Enter' && !e.shiftKey) { 
      e.preventDefault(); 
      handleSend(); 
    } 
  };

  const handleMic = () => {
    setListening(!isListening);
    if (!isListening) {
      setTimeout(() => { 
        sendMessage('Mere gehun mein peele patte kyon aa rahe hain?'); 
        setListening(false); 
      }, 2000);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100dvh', background: 'var(--color-bg-primary)', fontFamily: "'Inter', sans-serif" }}>

      {/* CHAT HEADER */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 32px', height: '76px', background: 'var(--color-bg-secondary)',
        borderBottom: '1px solid rgba(0,0,0,0.04)',
        boxShadow: '0 4px 24px rgba(26,122,64,0.04)', flexShrink: 0, zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ 
            width: '46px', height: '46px', borderRadius: '16px', 
            background: 'linear-gradient(135deg, #0F4C2A, #1A7A40)', 
            display: 'flex', alignItems: 'center', justifyContent: 'center', 
            boxShadow: '0 4px 12px rgba(26,122,64,0.25)' 
          }}>
            <Bot size={24} color="#fff" />
          </div>
          <div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, color: 'var(--color-text-primary)', fontSize: '1.1rem', letterSpacing: '-0.01em' }}>
              FasalSaathi AI
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              <span style={{ position: 'relative', display: 'flex', width: '8px', height: '8px' }}>
                <span style={{ position: 'absolute', width: '100%', height: '100%', borderRadius: '50%', background: '#22C55E', opacity: 0.7, animation: 'ping 2s cubic-bezier(0,0,0.2,1) infinite' }} />
                <span style={{ position: 'relative', width: '8px', height: '8px', borderRadius: '50%', background: '#22C55E' }} />
              </span>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>
                {isThinking ? 'Analyzing your request...' : 'Online & Ready'}
              </span>
            </div>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--color-section-header-bg)', borderRadius: '24px', padding: '8px 16px', border: '1px solid rgba(26,122,64,0.1)' }}>
          <Sparkles size={16} color="var(--color-accent-primary)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-accent-primary)', letterSpacing: '0.02em' }}>Gemini Powered</span>
        </div>
      </div>

      {/* MESSAGES AREA */}
      <div style={{ 
        flex: 1, overflowY: 'auto', padding: '32px 40px', 
        display: 'flex', flexDirection: 'column', gap: '24px', 
        scrollbarWidth: 'none' 
      }}>
        {/* Welcome message if empty */}
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px 24px', margin: 'auto', maxWidth: '480px' }}>
            <div style={{ 
              width: '80px', height: '80px', borderRadius: '24px', 
              background: 'linear-gradient(135deg, #0F4C2A, #1A7A40)', 
              display: 'flex', alignItems: 'center', justifyContent: 'center', 
              margin: '0 auto 24px', boxShadow: '0 8px 32px rgba(26,122,64,0.3)' 
            }}>
              <Bot size={36} color="#fff" />
            </div>
            <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '1.75rem', fontWeight: 800, color: 'var(--color-text-primary)', margin: '0 0 12px' }}>
              Namaste! 🌾
            </h2>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '1.05rem', lineHeight: 1.6, margin: 0 }}>
              Main FasalSaathi AI hoon. Aapki fasal, mandi, ya mausam ke baare mein mujhe kuch bhi poochhein.
            </p>
          </div>
        )}

        {messages.filter(msg => !msg.isHidden).map((msg, i) => {
          const isUser = msg.role === 'user';
          return (
            <div key={i} style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', gap: '16px', alignItems: 'flex-end' }}>
              {!isUser && (
                <div style={{ 
                  width: '36px', height: '36px', borderRadius: '12px', 
                  background: 'linear-gradient(135deg, #0F4C2A, #1A7A40)', 
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                  boxShadow: '0 4px 12px rgba(26,122,64,0.2)' 
                }}>
                  <Leaf size={16} color="#fff" />
                </div>
              )}
              
              <div style={{
                maxWidth: '75%',
                background: isUser ? 'linear-gradient(135deg, #1A7A40, #2D8F55)' : 'var(--color-bg-secondary)',
                color: isUser ? '#fff' : 'var(--color-text-primary)',
                borderRadius: isUser ? '20px 20px 4px 20px' : '4px 20px 20px 20px',
                padding: '16px 20px',
                boxShadow: isUser ? '0 8px 24px rgba(26,122,64,0.25)' : '0 4px 20px rgba(0,0,0,0.05)',
                border: isUser ? 'none' : '1px solid rgba(0,0,0,0.04)',
                fontSize: '0.95rem',
                lineHeight: 1.65,
                fontWeight: 500,
              }}>
                <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.content}</p>
                <div style={{ 
                  marginTop: '8px', fontSize: '0.75rem', 
                  color: isUser ? 'rgba(255,255,255,0.7)' : 'var(--color-text-secondary)',
                  textAlign: isUser ? 'right' : 'left', fontWeight: 600
                }}>
                  {new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          );
        })}

        {/* Thinking Indicator */}
        {isThinking && (
          <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '12px', background: 'linear-gradient(135deg, #0F4C2A, #1A7A40)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Leaf size={16} color="#fff" />
            </div>
            <div style={{ background: 'var(--color-bg-secondary)', borderRadius: '4px 20px 20px 20px', padding: '20px 24px', display: 'flex', gap: '8px', alignItems: 'center', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
              {[0, 1, 2].map(i => (
                <span key={i} style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--color-accent-primary)', display: 'inline-block', opacity: 0.6, animation: `bounce 1.4s ${i * 0.2}s infinite ease-in-out both` }} />
              ))}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* FOOTER AREA (Suggestions + Input) */}
      <div style={{ 
        background: 'var(--color-bg-secondary)', 
        borderTop: '1px solid rgba(0,0,0,0.04)', 
        padding: '16px 32px 24px', flexShrink: 0,
        boxShadow: '0 -4px 32px rgba(0,0,0,0.03)'
      }}>
        
        {/* Quick Suggestions Row */}
        <div style={{ display: 'flex', gap: '12px', overflowX: 'auto', scrollbarWidth: 'none', marginBottom: '20px', paddingBottom: '4px' }}>
          {suggestions.map((s, i) => (
            <button 
              key={i} 
              onClick={() => sendMessage(s)} 
              disabled={isThinking} 
              style={{ 
                flexShrink: 0, padding: '10px 18px', borderRadius: '24px', 
                border: '1.5px solid var(--color-border)', background: 'var(--color-bg-primary)', 
                color: 'var(--color-text-secondary)', fontSize: '0.85rem', fontWeight: 600, 
                cursor: 'pointer', whiteSpace: 'nowrap', transition: 'all 0.2s cubic-bezier(0.4,0,0.2,1)',
              }}
              onMouseEnter={e => { e.target.style.borderColor = 'var(--color-accent-primary)'; e.target.style.color = 'var(--color-accent-primary)'; e.target.style.background = 'var(--color-section-header-bg)'; e.target.style.transform = 'translateY(-2px)'; }}
              onMouseLeave={e => { e.target.style.borderColor = 'var(--color-border)'; e.target.style.color = 'var(--color-text-secondary)'; e.target.style.background = 'var(--color-bg-primary)'; e.target.style.transform = ''; }}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Input Bar Structure */}
        <div style={{ 
          display: 'flex', alignItems: 'flex-end', gap: '12px', 
          background: 'var(--color-bg-primary)', borderRadius: '24px', 
          padding: '8px 8px 8px 16px', border: '1.5px solid var(--color-border)', 
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.02)', transition: 'border-color 0.2s, box-shadow 0.2s' 
        }}
        onFocusCapture={e => { e.currentTarget.style.borderColor = 'var(--color-accent-primary)'; e.currentTarget.style.boxShadow = '0 0 0 4px rgba(26,122,64,0.1)'; }}
        onBlurCapture={e => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'inset 0 2px 4px rgba(0,0,0,0.02)'; }}>
          
          {/* Left Mic Button */}
          <button 
            onClick={handleMic} 
            style={{ 
              width: '44px', height: '44px', borderRadius: '50%', border: 'none', 
              background: isListening ? '#FEE2E2' : 'transparent', 
              display: 'flex', alignItems: 'center', justifyContent: 'center', 
              cursor: 'pointer', transition: 'all 0.2s', flexShrink: 0,
              color: isListening ? '#DC2626' : 'var(--color-text-secondary)'
            }}
            onMouseEnter={e => !isListening && (e.currentTarget.style.background = 'rgba(0,0,0,0.04)')}
            onMouseLeave={e => !isListening && (e.currentTarget.style.background = 'transparent')}
          >
            {isListening ? <MicOff size={22} /> : <Mic size={22} />}
          </button>

          {/* Text Area */}
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            disabled={isThinking}
            placeholder="Kheti ke baare mein poocho..."
            rows={1}
            style={{ 
              flex: 1, border: 'none', background: 'transparent', resize: 'none', outline: 'none', 
              fontFamily: "'Inter', sans-serif", fontSize: '1rem', color: 'var(--color-text-primary)', 
              maxHeight: '140px', lineHeight: 1.5, padding: '10px 4px', fontWeight: 500
            }}
          />

          {/* Right Send Button */}
          <button 
            onClick={handleSend} 
            disabled={!input.trim() || isThinking} 
            style={{ 
              width: '44px', height: '44px', borderRadius: '50%', border: 'none', 
              background: input.trim() && !isThinking ? 'linear-gradient(135deg, #1A7A40, #2D8F55)' : 'var(--color-border)', 
              display: 'flex', alignItems: 'center', justifyContent: 'center', 
              cursor: input.trim() && !isThinking ? 'pointer' : 'not-allowed', 
              transition: 'all 0.2s', flexShrink: 0,
              boxShadow: input.trim() && !isThinking ? '0 4px 12px rgba(26,122,64,0.3)' : 'none'
            }}
            onMouseEnter={e => input.trim() && !isThinking && (e.currentTarget.style.transform = 'scale(1.05)')}
            onMouseLeave={e => input.trim() && !isThinking && (e.currentTarget.style.transform = '')}
          >
            <Send size={20} color="#fff" style={{ transform: 'translateX(-1px) translateY(1px)' }} />
          </button>
        </div>
      </div>

      <style>{`
        @keyframes ping {
          0% { transform: scale(1); opacity: 1; }
          75%, 100% { transform: scale(2); opacity: 0; }
        }
        @keyframes bounce { 
          0%, 80%, 100% { transform: scale(0); } 
          40% { transform: scale(1); } 
        }
      `}</style>
    </div>
  );
};

export { ChatPage };
