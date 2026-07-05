// components/ScoreCard.jsx — 5-dimension lead score visualization
import React, { useState } from 'react';
import { useScore } from '../hooks/useScore';

const DIMENSIONS = [
  { key: 'icp_fit',         label: 'ICP Fit',        weight: '30%', icon: '🏢' },
  { key: 'intent_signals',  label: 'Intent Signals',  weight: '25%', icon: '🎯' },
  { key: 'timeline',        label: 'Timeline',        weight: '20%', icon: '⏱️' },
  { key: 'authority',       label: 'Authority',       weight: '15%', icon: '👑' },
  { key: 'engagement',      label: 'Engagement',      weight: '10%', icon: '💬' },
];

function ScoreBar({ value, gradient, delay = 0 }) {
  return (
    <div className="score-bar-track">
      <div
        className="score-bar-fill"
        style={{
          background: gradient,
          width: `${value}%`,
          animationDelay: `${delay}s`,
          '--target-width': `${value}%`,
        }}
      />
    </div>
  );
}

export default function ScoreCard({ scoreData, conversationId, onQualify }) {
  const { getScoreColor, getScoreGradient, getScoreLabel, isQualifying, qualifyLead, qualifyResult } = useScore();
  const [showQualify, setShowQualify] = useState(false);
  const [leadEmail, setLeadEmail] = useState('');
  const [leadCompany, setLeadCompany] = useState('');

  if (!scoreData) return null;

  const { overall_score, breakdown, reasoning } = scoreData;
  const gradient = getScoreGradient(overall_score);
  const { label, badge, action } = getScoreLabel(overall_score);
  const isHot = overall_score >= 75;

  const handleQualify = async () => {
    const result = await qualifyLead(conversationId, {
      email: leadEmail,
      company: leadCompany,
    });
    if (result && onQualify) onQualify(result);
    setShowQualify(false);
  };

  return (
    <div className="animate-slide-up" style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f0f4ff' }}>Lead Score</h3>
        <span className={`badge ${badge}`}>{label}</span>
      </div>

      {/* Big Score Circle */}
      <div style={{ textAlign: 'center', padding: '20px 0' }}>
        <div style={{
          display: 'inline-flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          width: '130px', height: '130px', borderRadius: '50%',
          background: `conic-gradient(${getScoreColor(overall_score)} ${overall_score * 3.6}deg, rgba(255,255,255,0.06) 0deg)`,
          position: 'relative',
          boxShadow: isHot ? `0 0 40px ${getScoreColor(overall_score)}44` : 'none',
          animation: isHot ? 'glow-pulse 2s ease-in-out infinite' : 'none',
        }}>
          <div style={{
            position: 'absolute', inset: '8px', borderRadius: '50%',
            background: 'var(--bg-secondary)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          }}>
            <span style={{
              fontSize: '2.2rem', fontWeight: 800, lineHeight: 1,
              background: gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              animation: 'scoreCount 0.5s ease forwards',
            }}>
              {overall_score}
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 500 }}>/ 100</span>
          </div>
        </div>
      </div>

      {/* Dimension Breakdown */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {DIMENSIONS.map(({ key, label, weight, icon }, i) => {
          const val = breakdown?.[key] ?? 0;
          return (
            <div key={key} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', gap: '5px', alignItems: 'center' }}>
                  <span>{icon}</span> {label}
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>({weight})</span>
                </span>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: getScoreColor(val) }}>{val}</span>
              </div>
              <ScoreBar value={val} gradient={gradient} delay={i * 0.1} />
            </div>
          );
        })}
      </div>

      {/* Reasoning */}
      {reasoning && (
        <div style={{
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: '10px', padding: '12px',
          fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.6,
        }}>
          <span style={{ color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: '4px' }}>💡 AI Reasoning</span>
          {reasoning}
        </div>
      )}

      {/* CTA Buttons */}
      {!qualifyResult && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: 'auto' }}>
          {!showQualify ? (
            <button className="btn-primary" onClick={() => setShowQualify(true)}
              style={{ width: '100%', padding: '12px' }}>
              {action} →
            </button>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <input
                className="chat-input" placeholder="Lead email (optional)"
                value={leadEmail} onChange={e => setLeadEmail(e.target.value)}
                style={{ fontSize: '0.85rem', padding: '10px 14px' }}
              />
              <input
                className="chat-input" placeholder="Company (optional)"
                value={leadCompany} onChange={e => setLeadCompany(e.target.value)}
                style={{ fontSize: '0.85rem', padding: '10px 14px' }}
              />
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn-ghost" onClick={() => setShowQualify(false)} style={{ flex: 1 }}>Cancel</button>
                <button className="btn-primary" onClick={handleQualify} disabled={isQualifying} style={{ flex: 2 }}>
                  {isQualifying ? 'Syncing...' : '✓ Confirm & Sync'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Qualify Success */}
      {qualifyResult && (
        <div style={{
          background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)',
          borderRadius: '10px', padding: '12px', textAlign: 'center',
          color: '#34d399', fontSize: '0.85rem', fontWeight: 600,
        }}>
          ✅ Lead synced to CRM! {qualifyResult.hubspot_contact_id ? '→ HubSpot' : '→ DB'} <br/>
          <span style={{ fontSize: '0.75rem', fontWeight: 400, color: 'rgba(52,211,153,0.7)' }}>{qualifyResult.message}</span>
        </div>
      )}
    </div>
  );
}
