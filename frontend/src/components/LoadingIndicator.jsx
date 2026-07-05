// components/LoadingIndicator.jsx — Animated typing dots
import React from 'react';

export default function LoadingIndicator() {
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-end', gap: '10px',
      marginBottom: '16px', animation: 'fadeInLeft 0.3s ease forwards',
    }}>
      {/* Bot avatar */}
      <div style={{
        width: '34px', height: '34px', borderRadius: '50%',
        background: 'linear-gradient(135deg, #0f1629, #1e293b)',
        border: '1px solid rgba(255,255,255,0.12)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '16px', flexShrink: 0,
      }}>🤖</div>

      {/* Typing bubble */}
      <div style={{
        background: 'rgba(255,255,255,0.06)',
        border: '1px solid rgba(255,255,255,0.09)',
        borderRadius: '18px 18px 18px 4px',
        padding: '14px 20px',
        display: 'flex', gap: '6px', alignItems: 'center',
      }}>
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  );
}
