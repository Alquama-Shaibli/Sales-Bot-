// components/ChatWidget.jsx — Main chat interface
import React, { useRef, useEffect, useState, useCallback } from 'react';
import Message from './Message';
import LoadingIndicator from './LoadingIndicator';
import ScoreCard from './ScoreCard';
import { useChat } from '../hooks/useChat';
import { useScore } from '../hooks/useScore';

const SEND_ICON = (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const SCORE_ICON = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
  </svg>
);

export default function ChatWidget() {
  const { messages, conversationId, isLoading, isStarting, isStarted, error, turnCount, startConversation, sendMessage, resetChat } = useChat();
  const { scoreData, isScoring, scoreConversation, resetScore } = useScore();

  const [inputText, setInputText]     = useState('');
  const [showScore, setShowScore]     = useState(false);
  const messagesEndRef                = useRef(null);
  const inputRef                      = useRef(null);
  const canScore                      = turnCount >= 3;

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Focus input after start
  useEffect(() => {
    if (isStarted && !isLoading) inputRef.current?.focus();
  }, [isStarted, isLoading]);

  const handleSend = useCallback(async () => {
    if (!inputText.trim() || isLoading) return;
    const text = inputText;
    setInputText('');
    await sendMessage(text);
  }, [inputText, isLoading, sendMessage]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleScore = useCallback(async () => {
    setShowScore(true);
    if (!scoreData) await scoreConversation(conversationId);
  }, [scoreData, scoreConversation, conversationId]);

  const handleReset = useCallback(() => {
    resetChat();
    resetScore();
    setShowScore(false);
    setInputText('');
  }, [resetChat, resetScore]);

  return (
    <div style={{
      display: 'flex', gap: '20px', height: '100%',
      flexDirection: window.innerWidth < 768 ? 'column' : 'row',
    }}>

      {/* ── LEFT: Chat Panel ─────────────────────────────── */}
      <div className="glass-card" style={{
        flex: showScore ? '1 1 60%' : '1 1 100%',
        display: 'flex', flexDirection: 'column',
        overflow: 'hidden', transition: 'flex 0.4s ease',
        minHeight: '500px',
      }}>

        {/* Chat Header */}
        <div style={{
          padding: '18px 22px', borderBottom: '1px solid rgba(255,255,255,0.07)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          background: 'rgba(0,0,0,0.2)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '36px', height: '36px', borderRadius: '10px',
              background: 'linear-gradient(135deg, #4f8ef7, #7c3aed)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px',
            }}>🤖</div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>Sales Assistant</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: isStarted ? '#10b981' : '#475569', display: 'inline-block' }} />
                {isStarted ? `Active · Turn ${turnCount}` : 'Ready to start'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            {isStarted && canScore && !showScore && (
              <button className="btn-ghost" onClick={handleScore} disabled={isScoring}
                style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', padding: '8px 14px' }}>
                {SCORE_ICON} {isScoring ? 'Scoring...' : 'Get Score'}
              </button>
            )}
            {isStarted && (
              <button className="btn-ghost" onClick={handleReset}
                style={{ fontSize: '0.8rem', padding: '8px 14px' }}>
                ↺ Reset
              </button>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div style={{
          flex: 1, overflowY: 'auto', padding: '20px 22px',
          display: 'flex', flexDirection: 'column',
        }}>
          {/* Welcome Screen */}
          {!isStarted && (
            <div style={{
              flex: 1, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: '20px',
              animation: 'fadeIn 0.5s ease forwards',
            }}>
              <div style={{
                width: '80px', height: '80px', borderRadius: '24px',
                background: 'linear-gradient(135deg, #4f8ef7, #7c3aed)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '36px',
                boxShadow: '0 0 40px rgba(79,142,247,0.3)',
              }}>🤖</div>
              <div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '8px' }}>EnterpriseLead AI</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '300px', lineHeight: 1.6 }}>
                  Qualify your B2B leads through natural conversation — scored in real-time across 5 dimensions.
                </p>
              </div>
              <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', justifyContent: 'center' }}>
                {['⚡ 2-minute qualification', '🎯 5-dimension scoring', '🔗 HubSpot sync'].map(f => (
                  <span key={f} style={{
                    background: 'rgba(79,142,247,0.1)', border: '1px solid rgba(79,142,247,0.2)',
                    borderRadius: '99px', padding: '6px 14px', fontSize: '0.78rem', color: '#93c5fd',
                  }}>{f}</span>
                ))}
              </div>
              <button
                id="start-conversation-btn"
                className="btn-primary" onClick={startConversation} disabled={isStarting}
                style={{ padding: '14px 36px', fontSize: '1rem' }}>
                {isStarting ? 'Starting...' : '▶ Start Conversation'}
              </button>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg) => (
            <Message key={msg.id} message={msg} />
          ))}

          {/* Typing indicator */}
          {isLoading && <LoadingIndicator />}

          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        {isStarted && (
          <div style={{
            padding: '14px 18px', borderTop: '1px solid rgba(255,255,255,0.07)',
            display: 'flex', gap: '10px', alignItems: 'flex-end',
            background: 'rgba(0,0,0,0.15)',
          }}>
            <textarea
              id="chat-input-field"
              ref={inputRef}
              className="chat-input"
              placeholder="Type your message... (Enter to send)"
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              style={{
                flex: 1, minHeight: '44px', maxHeight: '120px',
                resize: 'none', overflowY: 'auto',
              }}
            />
            <button
              id="send-message-btn"
              className="btn-primary"
              onClick={handleSend}
              disabled={!inputText.trim() || isLoading}
              style={{ padding: '12px 16px', flexShrink: 0 }}>
              {SEND_ICON}
            </button>
          </div>
        )}

        {/* Score prompt */}
        {isStarted && canScore && !showScore && !isLoading && (
          <div style={{
            padding: '10px 18px', borderTop: '1px solid rgba(255,255,255,0.05)',
            background: 'rgba(79,142,247,0.05)',
            display: 'flex', justifyContent: 'center',
          }}>
            <span style={{ fontSize: '0.78rem', color: 'rgba(147,197,253,0.8)' }}>
              ✨ {turnCount} exchanges collected — ready to score this lead!
              <button onClick={handleScore} style={{ background: 'none', border: 'none', color: '#93c5fd', cursor: 'pointer', marginLeft: '6px', fontWeight: 600, textDecoration: 'underline' }}>
                Score now
              </button>
            </span>
          </div>
        )}
      </div>

      {/* ── RIGHT: Score Panel ────────────────────────────── */}
      {showScore && (
        <div className="glass-card animate-slide-up" style={{
          flex: '0 0 340px', padding: '20px', overflowY: 'auto',
        }}>
          {isScoring ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-secondary)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⚡</div>
              <div style={{ fontWeight: 600 }}>Analyzing conversation...</div>
              <div style={{ fontSize: '0.8rem', marginTop: '8px', color: 'var(--text-muted)' }}>Claude is scoring this lead</div>
            </div>
          ) : (
            <ScoreCard scoreData={scoreData} conversationId={conversationId} />
          )}
        </div>
      )}
    </div>
  );
}
