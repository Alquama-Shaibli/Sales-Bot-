// components/Message.jsx — Individual message bubble
import React, { memo } from 'react';

const BOT_AVATAR = '🤖';
const USER_AVATAR = '👤';

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  } catch { return ''; }
}

const Message = memo(({ message }) => {
  const isUser = message.role === 'user';
  const isError = message.isError;

  return (
    <div
      className="animate-fade-in"
      style={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-end',
        gap: '10px',
        marginBottom: '16px',
        animation: isUser ? 'fadeInRight 0.3s ease forwards' : 'fadeInLeft 0.3s ease forwards',
      }}
    >
      {/* Avatar */}
      <div style={{
        width: '34px', height: '34px',
        borderRadius: '50%',
        background: isUser
          ? 'linear-gradient(135deg, #4f8ef7, #7c3aed)'
          : 'linear-gradient(135deg, #0f1629, #1e293b)',
        border: '1px solid rgba(255,255,255,0.12)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '16px', flexShrink: 0,
      }}>
        {isUser ? USER_AVATAR : BOT_AVATAR}
      </div>

      {/* Bubble */}
      <div style={{ maxWidth: '72%', display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start' }}>
        <div style={{
          background: isUser
            ? 'linear-gradient(135deg, #4f8ef7 0%, #7c3aed 100%)'
            : isError
              ? 'rgba(239,68,68,0.12)'
              : 'rgba(255,255,255,0.06)',
          border: isUser
            ? 'none'
            : isError
              ? '1px solid rgba(239,68,68,0.25)'
              : '1px solid rgba(255,255,255,0.09)',
          borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
          padding: '12px 16px',
          color: isError ? '#f87171' : '#f0f4ff',
          fontSize: '0.9rem',
          lineHeight: '1.55',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          boxShadow: isUser ? '0 4px 20px rgba(79,142,247,0.25)' : '0 2px 12px rgba(0,0,0,0.25)',
        }}>
          {message.content}
        </div>

        {/* Timestamp */}
        <span style={{ fontSize: '0.7rem', color: 'rgba(148,163,184,0.6)', marginTop: '4px', padding: '0 4px' }}>
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
});

Message.displayName = 'Message';
export default Message;
